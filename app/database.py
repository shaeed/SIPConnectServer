
import json
import os
from typing import List, Optional

# For this simple application, lets use file as database
DB_FILE = os.path.join('app', 'data.json')

# global variable to cache the db entries
_DB_FULL: dict = {}
_DB_DATA: List[dict] = [] # All users

def load_data() -> List[dict]:
    global _DB_FULL
    global _DB_DATA

    if _DB_DATA and _DB_FULL:
        return _DB_DATA
    if not os.path.exists(DB_FILE):
        return []
    with open(DB_FILE, 'r') as file:
        _DB_FULL = json.load(file)
        _DB_DATA = _DB_FULL['users']
        return _DB_DATA

def save_data(data: List[dict] = None):
    global _DB_DATA

    if data is not None:
        _DB_FULL['users'] = data
        _DB_DATA = data

    with open(DB_FILE, 'w') as file:
        json.dump(_DB_FULL, file, indent=2)

def get_all_users() -> List[dict]:
    return load_data()

def get_user_data(user_name) -> Optional[dict]:
    data = get_all_users()
    for user in data:
        if user['user_name'] == user_name:
            return user
    return None

def add_or_update_user(new_user: dict) -> str:
    users = get_all_users()
    for i, user in enumerate(users):
        if user['user_name'] == new_user['user_name']:
            users[i].update(new_user)
            save_data(users)
            return "Updated existing user."
    users.append(new_user)
    save_data(users)
    return "Added new user."

def delete_user(user_name) -> str:
    users = get_all_users()
    new_data = [d for d in users if d['user_name'] != user_name]
    if len(users) == len(new_data):
        return "User not found."
    save_data(new_data)
    return "User deleted."

def update_fcm_token(user_name: str, device_id: str, new_fcm_token: str) -> str:
    user_data = get_user_data(user_name)
    if not user_data:
        return f"No device found with user_name '{user_name}'."

    if not user_data.get('devices'):
        user_data['devices'] = {}
    user_data['devices'].update({
        device_id: {
            'device_id': device_id,
            'fcm_token': new_fcm_token
        }
    })
    save_data()
    return f"FCM token updated for user '{user_name}'."

def get_fcm_tokens(user_name: str) -> List[str]:
    user_data = get_user_data(user_name)
    tokens = [x['fcm_token'] for x in user_data['devices'].values()]
    return tokens

def update_oauth2_token(user_name: str, new_oauth2_token: str, expiry: int):
    user_data = get_user_data(user_name)
    if not user_data:
        return f"No device found with user_name '{user_name}'."

    user_data['oauth2_token'] = new_oauth2_token
    user_data['oauth2_token_expiry'] = expiry
    save_data()
    return f"OAuth2 token updated for user '{user_name}'."

def get_oauth2_token(user_name: str) -> dict:
    user_data = get_user_data(user_name)
    if not user_data:
        return {}

    return {
        "oauth2_token": user_data.get("oauth2_token"),
        "oauth2_token_expiry": user_data.get("oauth2_token_expiry", 0)
    }

def user_exits(user_name: str) -> bool:
    all_devs = get_all_users()
    return any(filter(lambda x: x['user_name'] == user_name, all_devs))

def get_project_id() -> str:
    return _DB_FULL['app-config']['firebase_project_id']

def set_project_id(project_id: str):
    _DB_FULL['app-config']['firebase_project_id'] = project_id
    save_data()

def get_service_account_file_path() -> str:
    return _DB_FULL['app-config']['service_account_file']

def set_service_account_file_path(sa_path: str):
    _DB_FULL['app-config']['service_account_file'] = sa_path
    save_data()

def add_dummy_user():
    data = get_all_users()
    data.append({
        "user_name": "dummy_user",
        "user_pass": "test_pass",
        "oauth2_token": "test_token",
        "oauth2_token_expiry": 12345,
        "devices": {
            "dummy_device": {
                "device_id": "dummy_device",
                "fcm_token": "cRwxVa0NT_qx4P8T1Ee1PQ:APA91bFs6OlKgeK4mx9cMQ34PrO8moxsoD6gsu6WlZF8RGItlhNoiO8HPkReiu4vS10AgKATisIBsmi2GuGozZkGABChazdNGxaKuo8qS6H6xkI3sZwqmTE"
            }
        }
    })
    save_data(data)
