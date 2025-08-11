#!/usr/bin/env python3
import json
import sys, base64, requests

caller = sys.argv[1]
body_b64 = sys.argv[2]
user = sys.argv[3]
body = base64.b64decode(body_b64).decode('utf-8')

data = {
    "username": user,
    "phone_number": caller,
    "body": body
}

# todo change it to sqlite db insert
with open('/app/tmp.sms', 'a') as f:
    f.write(f"{json.dumps(data)}\n")

response = requests.post(
    "http://localhost:8000/sip/alert/sms",
    headers={"Content-Type": "application/json"},
    json=data
)

print(f"-- POST Response: {response.status_code} {response.text}")
