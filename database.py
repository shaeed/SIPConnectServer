
import json
import os
from typing import List

# For this simple application, lets use file as database
DB_FILE = r'data.json'

# global variable to cache the db entries
_DB_DATA: List[dict] = []

def load_data() -> List[dict]:
    global _DB_DATA
    if _DB_DATA:
        return _DB_DATA
    if not os.path.exists(DB_FILE):
        return []
    with open(DB_FILE, 'r') as file:
        print('reading db')
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
    print('New deice:', new_device)
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

# Test usage:
if __name__ == "__main__":
    DB_FILE = r'test_data.json'
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)

    # Add new device
    resp = add_or_update_device({
        "device_id": "dev1",
        "user_name": "user1",
        "user_pass": "pass1",
        "fcm_token": "fcm1",
        "oauth2_token": "token1"
    })
    assert resp == "Added new device."

    # Get all devices
    all_devices = get_all_devices()
    assert len(all_devices) == 1
    assert all_devices[0]['user_name'] == "user1"

    # Get device by user_name
    device = get_device("user1")
    assert device is not None
    assert device['user_pass'] == "pass1"

    # Update FCM token
    resp = update_fcm_token("user1", "new_fcm_token")
    assert resp.startswith("FCM token updated")
    device = get_device("user1")
    assert device['fcm_token'] == "new_fcm_token"

    # Update OAuth2 token
    resp = update_oauth2_token("user1", "new_oauth_token", 10)
    assert resp.startswith("OAuth2 token updated")
    device = get_device("user1")
    assert device['oauth2_token'] == "new_oauth_token"
    assert isinstance(device['oauth2_token_expiry'], int)

    # Get OAuth2 token
    oauth_info = get_oauth2_token("user1")
    assert oauth_info['oauth2_token'] == "new_oauth_token"
    assert isinstance(oauth_info['oauth2_token_expiry'], int)

    # Get OAuth2 token (not found)
    oauth_info = get_oauth2_token("user2")
    assert not oauth_info

    # User exits
    resp = user_exits('user1')
    assert resp

    # User not exits
    resp = user_exits('user2')
    assert not resp

    # Delete device
    resp = delete_device("user1")
    assert resp == "Device deleted."
    assert get_device("user1") is None

    # Delete non-existent device
    resp = delete_device("unknown")
    assert resp == "Device not found."

    # Clean up test file
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)

    print("✅ All tests passed.")
