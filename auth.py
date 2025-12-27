import bcrypt
import jwt
import datetime
from config import SECRET_KEY
from database import get_user, create_user

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed)

def generate_token(username):
    payload = {
        "username": username,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def authenticate(action, username, password):
    user = get_user(username)

    if action == "REGISTER":
        if user:
            return None, "User already exists"
        create_user(username, hash_password(password))
        return generate_token(username), None

    if action == "LOGIN":
        if not user or not verify_password(password, user[0]):
            return None, "Invalid credentials"
        return generate_token(username), None

    return None, "Invalid action"