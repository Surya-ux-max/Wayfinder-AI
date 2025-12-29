from flask import Flask, request, jsonify
from flask_cors import CORS

from resume_parser import extract_text_from_pdf
from agent import analyze_career_profile, handle_feature_question

app = Flask(__name__)
CORS(app)


@app.route("/", methods=["GET"])
def home():
    return "Backend is running"


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

    mode = data.get("mode", "ask")
    question = data["question"]

    answer = handle_feature_question(mode, question)
    return jsonify({"answer": answer})


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True)
    app.run(host="0.0.0.0", port=port)