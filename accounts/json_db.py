import json
from pathlib import Path
from django.contrib.auth.hashers import make_password, check_password

DB = Path("data/db.json")

def load():
    return json.loads(DB.read_text()) if DB.exists() else {"users": []}

def save(data):
    DB.parent.mkdir(exist_ok=True)
    DB.write_text(json.dumps(data, indent=2))

def create_user(username, email, password):
    data = load()
    hashed_password = make_password(password)
    new_user = {
        "username": username,
        "email": email,
        "password": hashed_password
    }
    data["users"].append(new_user)
    save(data)
    return new_user

def authenticate_user(username, password):
    data = load()
    for user in data["users"]:
        if user["username"] == username:
            if check_password(password, user["password"]):
                return user
    return None