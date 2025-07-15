
import json
import os
from typing import List

# For this simple application, lets use file as database
DB_FILE = os.path.join('app', 'data.json')

# global variable to cache the db entries
_DB_DATA: List[dict] = []

def load_data() -> List[dict]:
    global _DB_DATA
    if _DB_DATA:
        return _DB_DATA
    if not os.path.exists(DB_FILE):
        return []
    with open(DB_FILE, 'r') as file:
        _DB_DATA = json.load(file)
        return _DB_DATA


def save_data(data):
    global _DB_DATA
    with open(DB_FILE, 'w') as file:
        json.dump(data, file, indent=2)
    _DB_DATA = data

def get_all_devices():
    return load_data()

def get_device(user_name):
    data = load_data()
    for device in data:
        if device['user_name'] == user_name:
            return device
    return None

def add_or_update_device(new_device: dict):
    data = load_data()
    for i, device in enumerate(data):
        if device['user_name'] == new_device['user_name']:
            data[i].update(new_device)
            save_data(data)
            return "Updated existing device."
    data.append(new_device)
    save_data(data)
    return "Added new device."

def delete_device(user_name):
    data = load_data()
    new_data = [d for d in data if d['user_name'] != user_name]
    if len(data) == len(new_data):
        return "Device not found."
    save_data(new_data)
    return "Device deleted."

def update_fcm_token(user_name, new_fcm_token):
    data = load_data()
    updated = False

    for device in data:
        if device['user_name'] == user_name:
            device['fcm_token'] = new_fcm_token
            updated = True

    if updated:
        save_data(data)
        return f"FCM token updated for user '{user_name}'."
    else:
        return f"No device found with user_name '{user_name}'."

def get_fcm_token(user_name: str) -> str:
    return get_device(user_name).get('fcm_token')

def update_oauth2_token(user_name: str, new_oauth2_token: str, expiry: int):
    data = load_data()
    updated = False

    for device in data:
        if device['user_name'] == user_name:
            device['oauth2_token'] = new_oauth2_token
            device['oauth2_token_expiry'] = expiry
            updated = True

    if updated:
        save_data(data)
        return f"OAuth2 token updated for user '{user_name}'."
    else:
        return f"No device found with user_name '{user_name}'."

def get_oauth2_token(user_name: str) -> dict:
    data = load_data()

    for device in data:
        if device['user_name'] == user_name:
            return {
                "oauth2_token": device.get("oauth2_token"),
                "oauth2_token_expiry": device.get("oauth2_token_expiry", 0)
            }
    # username not present
    return {}

def user_exits(user_name: str) -> bool:
    all_devs = get_all_devices()
    return any(filter(lambda x: x['user_name'] == user_name, all_devs))

def add_dummy_user():
    data = load_data()
    data.append({
        "device_id": "dummy_device",
        "user_name": "dummy_user",
        "user_pass": "test_pass",
        "fcm_token": "cRwxVa0NT_qx4P8T1Ee1PQ:APA91bFs6OlKgeK4mx9cMQ34PrO8moxsoD6gsu6WlZF8RGItlhNoiO8HPkReiu4vS10AgKATisIBsmi2GuGozZkGABChazdNGxaKuo8qS6H6xkI3sZwqmTE",
        "oauth2_token": "test_token",
        "oauth2_token_expiry": 12345
    })
    save_data(data)
