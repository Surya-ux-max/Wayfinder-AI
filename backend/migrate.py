from database import ChatDatabase
from datetime import datetime
from bson import ObjectId

def migrate_old_chats():
    db = ChatDatabase()
    
    # Get old chat collection
    old_chats = db.db.chat_history
    
    # Group old chats by user_id
    users = old_chats.distinct("user_id")
    
    for user_id in users:
        user_chats = list(old_chats.find({"user_id": user_id}).sort("timestamp", 1))
        
        if user_chats:
            # Create a session for this user's old chats
            first_chat = user_chats[0]
            title = first_chat["question"][:50] + "..." if len(first_chat["question"]) > 50 else first_chat["question"]
            
            session_data = {
                "user_id": user_id,
                "title": title,
                "created_at": first_chat["timestamp"],
                "updated_at": user_chats[-1]["timestamp"]
            }
            
            session_result = db.sessions.insert_one(session_data)
            session_id = session_result.inserted_id
            
            # Convert old chats to messages
            for chat in user_chats:
                message_data = {
                    "session_id": session_id,
                    "question": chat["question"],
                    "answer": chat["answer"],
                    "mode": chat.get("mode", "ask"),
                    "timestamp": chat["timestamp"]
                }
                db.messages.insert_one(message_data)
            
            print(f"Migrated {len(user_chats)} chats for user {user_id}")
    
    print("Migration completed!")

if __name__ == "__main__":
    migrate_old_chats()