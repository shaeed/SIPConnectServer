#!/usr/bin/env python3
import json
import sys, base64, requests
import sqlite3
import traceback

SQLite_FILE = r'/var/log/asterisk/master.db' # '/var/lib/asterisk/asterisk.db'


def call_api(payload: dict):
    response = requests.post(
        "http://localhost:8000/sip/alert/sms",
        headers={"Content-Type": "application/json"},
        json=payload
    )
    print(f"-- POST Response: {response.status_code} {response.text}")

def insert_in_db(payload: dict):
    # with open('/app/tmp.sms', 'a') as f:
    #     f.write(f"{json.dumps(payload)}\n")

    conn = sqlite3.connect(SQLite_FILE)
    cursor = conn.cursor()
    cursor.execute("""
            INSERT INTO sms_log (user, number, message)
            VALUES (?, ?, ?);
        """, (payload["username"], payload["phone_number"], payload["body"]))

    conn.commit()
    cursor.close()
    conn.close()

if __name__ == '__main__':
    caller = sys.argv[1]
    body_b64 = sys.argv[2]
    user = sys.argv[3]
    body = base64.b64decode(body_b64).decode('utf-8')

    data = {
        "username": user,
        "phone_number": caller,
        "body": body
    }
    try:
        call_api(data)
    except requests.RequestException:
        print('SMS alert api call failed.', traceback.print_exc())
    try:
        insert_in_db(data)
    except sqlite3.DatabaseError:
        print('DB Insert failed.', traceback.print_exc())
