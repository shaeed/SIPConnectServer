
import aiohttp
import asyncio
from app.database import get_fcm_tokens, add_dummy_user, delete_user
from app.oAuth2_generator import PROJECT_ID, get_oauth_token

async def push_call_alert(sip_user: str, phone_number: str, payload: dict = None):
    fcm_tokens = get_fcm_tokens(sip_user)
    oauth_token = get_oauth_token(sip_user)
    data = {"type": "call", "phone_number": phone_number}
    if payload and payload.get("type") == "missed":
        data["type"] = "missed-call"
    return await asyncio.gather(*[call_firebase_api(oauth_token, x, data) for x in fcm_tokens])

async def push_sms_alert(sip_user: str, phone_number: str, message_body: str):
    fcm_tokens = get_fcm_tokens(sip_user)
    oauth_token = get_oauth_token(sip_user)
    data = {"type": "sms", "phone_number": phone_number, "body": message_body}
    return await asyncio.gather(*[call_firebase_api(oauth_token, x, data) for x in fcm_tokens])


async def call_firebase_api(oauth_token: str, fcm_token: str, data: dict) -> (int, str):
    url = f"https://fcm.googleapis.com/v1/projects/{PROJECT_ID}/messages:send"

    headers = {
        "Authorization": f"Bearer {oauth_token}",
        "Content-Type": "application/json; UTF-8"
    }
    payload = {
        "message": {
            "token": fcm_token,
            "android": {"priority": "high"},
            "data": data
        }
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as response:
            status = response.status
            res_data = await response.json()
            # print("Status:", status, "Response:", res_data)
            return {'status': status, 'data': res_data}
