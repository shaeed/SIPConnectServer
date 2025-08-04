#!/usr/bin/env python3
import sys
import requests


caller = sys.argv[1]
body = sys.argv[2]
user = sys.argv[3]

data = {
    "username": user,
    "phone_number": caller,
    "body": body
}

response = requests.post(
    "http://localhost:8000/sip/alert/sms",
    headers={"Content-Type": "application/json"},
    json=data
)

print(f"-- POST Response: {response.status_code} {response.text}")
