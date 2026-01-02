import jwt
import os
from datetime import datetime, timedelta
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

class AuthManager:
    def __init__(self):
        self.client = MongoClient(os.getenv('MONGODB_URI'))
        self.db = self.client.wayfinder
        self.users = self.db.users
        self.secret = os.getenv('JWT_SECRET')

    def register_user(self, email, password, name):
        # Check if user exists
        if self.users.find_one({"email": email}):
            return {"error": "User already exists"}
        
        # Create user with plain text password
        user_data = {
            "email": email,
            "password": password,  # Plain text
            "name": name,
            "created_at": datetime.utcnow()
        }
        
        result = self.users.insert_one(user_data)
        user_id = str(result.inserted_id)
        
        # Generate token
        token = self.generate_token(user_id, email)
        
        return {
            "success": True,
            "token": token,
            "user": {"id": user_id, "email": email, "name": name}
        }

    def login_user(self, email, password):
        # Find user
        user = self.users.find_one({"email": email})
        if not user:
            return {"error": "Invalid credentials"}
        
        # Check password (plain text comparison)
        if user['password'] != password:
            return {"error": "Invalid credentials"}
        
        # Generate token
        user_id = str(user['_id'])
        token = self.generate_token(user_id, email)
        
        return {
            "success": True,
            "token": token,
            "user": {"id": user_id, "email": email, "name": user['name']}
        }

    def generate_token(self, user_id, email):
        payload = {
            "user_id": user_id,
            "email": email,
            "exp": datetime.utcnow() + timedelta(days=30)
        }
        return jwt.encode(payload, self.secret, algorithm='HS256')

    def verify_token(self, token):
        try:
            payload = jwt.decode(token, self.secret, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return {"error": "Token expired"}
        except jwt.InvalidTokenError:
            return {"error": "Invalid token"}