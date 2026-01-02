from flask import Flask, request, jsonify
from flask_cors import CORS

from resume_parser import extract_text_from_pdf
from agent import analyze_career_profile, handle_feature_question
from database import ChatDatabase
from auth import AuthManager

app = Flask(__name__)
CORS(app)
db = ChatDatabase()
auth = AuthManager()


@app.route("/", methods=["GET"])
def home():
    return "Backend is running"


# --------------------------------------------------
# Authentication Endpoints
# --------------------------------------------------
@app.route("/auth/register", methods=["POST"])
def register():
    data = request.get_json()
    
    if not data or not all(k in data for k in ['email', 'password', 'name']):
        return jsonify({"error": "Email, password, and name required"}), 400
    
    result = auth.register_user(data['email'], data['password'], data['name'])
    
    if 'error' in result:
        return jsonify(result), 400
    
    return jsonify(result)

@app.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json()
    print(f"Login request received: {data}")
    
    if not data or not all(k in data for k in ['email', 'password']):
        print("Missing email or password")
        return jsonify({"error": "Email and password required"}), 400
    
    print(f"Attempting login for email: {data['email']}")
    result = auth.login_user(data['email'], data['password'])
    print(f"Login result: {result}")
    
    if 'error' in result:
        return jsonify(result), 400
    
    return jsonify(result)


# --------------------------------------------------
# Authentication Helper
# --------------------------------------------------
def get_user_from_token():
    token = request.headers.get('Authorization')
    if not token:
        return None
    
    if token.startswith('Bearer '):
        token = token[7:]
    
    result = auth.verify_token(token)
    if 'error' in result:
        return None
    
    return result


# --------------------------------------------------
# Resume Analysis (ISOLATED)
# --------------------------------------------------
@app.route("/analyze", methods=["POST"])
def analyze():
    if "resume" not in request.files:
        return jsonify({"error": "Resume file is required"}), 400

    resume_file = request.files["resume"]
    job_description = request.form.get("job_description", "")

    resume_text = extract_text_from_pdf(resume_file)

    if not resume_text or len(resume_text.strip()) < 200:
        return jsonify({"error": "Invalid or empty resume"}), 400

    analysis = analyze_career_profile(resume_text, job_description)
    return jsonify({"career_analysis": analysis})


# --------------------------------------------------
# Feature-based Ask Endpoint
# --------------------------------------------------
@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()

    if not data or "question" not in data:
        return jsonify({"error": "Question is required"}), 400

    # Get user from token or use anonymous
    user = get_user_from_token()
    user_id = user['user_id'] if user else 'anonymous'
    
    mode = data.get("mode", "ask")
    question = data["question"]
    session_id = data.get("session_id")

    answer = handle_feature_question(mode, question)
    
    # Create new session if none provided
    if not session_id:
        session = db.create_session(user_id)
        session_id = str(session.inserted_id)
    
    # Save message to session
    try:
        db.save_message(session_id, question, answer, mode)
    except Exception as e:
        print(f"Failed to save message: {e}")
    
    return jsonify({"answer": answer, "session_id": session_id})


# --------------------------------------------------
# Chat History Endpoints
# --------------------------------------------------
@app.route("/chat/sessions/<user_id>", methods=["GET"])
def get_user_sessions(user_id):
    # Verify user can access these sessions
    user = get_user_from_token()
    if user and user['user_id'] != user_id:
        return jsonify({"error": "Unauthorized"}), 403
    
    print(f"Getting sessions for user: {user_id}")
    try:
        sessions = db.get_user_sessions(user_id)
        print(f"Found {len(sessions)} sessions")
        # Convert ObjectId to string for JSON serialization
        for session in sessions:
            if '_id' in session:
                session["_id"] = str(session["_id"])
        print(f"Sessions data: {sessions}")
        return jsonify({"sessions": sessions})
    except Exception as e:
        print(f"Error getting sessions: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/chat/session/<session_id>/messages", methods=["GET"])
def get_session_messages(session_id):
    try:
        messages = db.get_session_messages(session_id)
        # Convert ObjectId to string for JSON serialization
        for message in messages:
            message["_id"] = str(message["_id"])
            message["session_id"] = str(message["session_id"])
        return jsonify({"messages": messages})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/chat/session/<session_id>", methods=["DELETE"])
def delete_session(session_id):
    try:
        db.delete_session(session_id)
        return jsonify({"message": "Session deleted"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/migrate/<user_id>", methods=["POST"])
def migrate_user_chats(user_id):
    try:
        # Get old chats
        old_chats = list(db.db.chat_history.find({"user_id": user_id}).sort("timestamp", 1))
        
        if old_chats:
            # Create session
            first_chat = old_chats[0]
            title = first_chat["question"][:50] + "..." if len(first_chat["question"]) > 50 else first_chat["question"]
            session = db.create_session(user_id, title)
            session_id = str(session.inserted_id)
            
            # Move chats to messages
            for chat in old_chats:
                db.save_message(session_id, chat["question"], chat["answer"], chat.get("mode", "ask"))
            
            # Delete old chats
            db.db.chat_history.delete_many({"user_id": user_id})
            
            return jsonify({"message": f"Migrated {len(old_chats)} chats", "session_id": session_id})
        else:
            return jsonify({"message": "No old chats found"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/debug/users", methods=["GET"])
def debug_users():
    try:
        # Get all unique user IDs from chat_history
        users = db.db.chat_history.distinct("user_id")
        result = {}
        for user in users:
            count = db.db.chat_history.count_documents({"user_id": user})
            result[user] = count
        return jsonify({"users": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)