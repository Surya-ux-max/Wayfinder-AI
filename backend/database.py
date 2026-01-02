from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv
from bson import ObjectId

load_dotenv()

class ChatDatabase:
    def __init__(self):
        self.client = MongoClient(os.getenv('MONGODB_URI'))
        self.db = self.client.wayfinder
        self.sessions = self.db.chat_sessions
        self.messages = self.db.chat_messages

    def create_session(self, user_id, title="New Chat"):
        session_data = {
            "user_id": user_id,
            "title": title,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        return self.sessions.insert_one(session_data)

    def save_message(self, session_id, question, answer, mode="ask"):
        message_data = {
            "session_id": ObjectId(session_id),
            "question": question,
            "answer": answer,
            "mode": mode,
            "timestamp": datetime.utcnow()
        }
        result = self.messages.insert_one(message_data)
        
        # Update session title with first question
        session = self.sessions.find_one({"_id": ObjectId(session_id)})
        if session and session.get("title") == "New Chat":
            title = question[:50] + "..." if len(question) > 50 else question
            self.sessions.update_one(
                {"_id": ObjectId(session_id)},
                {"$set": {"title": title, "updated_at": datetime.utcnow()}}
            )
        
        return result

    def get_user_sessions(self, user_id):
        print(f"Database: Looking for sessions for user_id: {user_id}")
        sessions = list(self.sessions.find(
            {"user_id": user_id}
        ).sort("updated_at", -1))
        print(f"Database: Found {len(sessions)} sessions")
        
        # Fallback: if no sessions, check for old chat_history format
        if not sessions:
            print(f"Database: No sessions found, checking old chat_history")
            old_chats = self.db.chat_history
            old_chat_count = old_chats.count_documents({"user_id": user_id})
            print(f"Database: Found {old_chat_count} old chats for user {user_id}")
            
            if old_chat_count > 0:
                # Create a temporary session from old chats
                first_chat = old_chats.find_one({"user_id": user_id})
                print(f"Database: First old chat: {first_chat}")
                return [{
                    "_id": "legacy",
                    "title": "Legacy Chats (Click to migrate)",
                    "created_at": first_chat.get("timestamp", datetime.utcnow()),
                    "updated_at": first_chat.get("timestamp", datetime.utcnow())
                }]
        
        return sessions

    def get_session_messages(self, session_id):
        return list(self.messages.find(
            {"session_id": ObjectId(session_id)}
        ).sort("timestamp", 1))

    def delete_session(self, session_id):
        self.messages.delete_many({"session_id": ObjectId(session_id)})
        return self.sessions.delete_one({"_id": ObjectId(session_id)})