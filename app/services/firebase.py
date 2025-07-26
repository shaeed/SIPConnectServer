
import aiohttp
import asyncio
from app.database import get_fcm_tokens, get_project_id, get_fcm_tokens_with_device_id
from app.oAuth2_generator import get_oauth_token

async def push_call_alert(sip_user: str, phone_number: str, payload: dict = None):
    fcm_tokens = get_fcm_tokens(sip_user)
    oauth_token = get_oauth_token(sip_user)
    data = {"type": "call", "phone_number": phone_number}
    if payload and payload.get("type") == "missed":
        data["type"] = "missed-call"
    return await asyncio.gather(*[call_firebase_api(oauth_token, x, data) for x in fcm_tokens])

async def push_sms_alert(sip_user: str, phone_number: str, message_body: str, from_device: str = None):
    if from_device:
        token_dict = get_fcm_tokens_with_device_id(sip_user)
        fcm_tokens = [token_dict[x] for x in token_dict if x != from_device]
    else:
        fcm_tokens = get_fcm_tokens(sip_user)
    oauth_token = get_oauth_token(sip_user)
    data = {"type": "sms", "phone_number": phone_number, "body": message_body}
    return await asyncio.gather(*[call_firebase_api(oauth_token, x, data) for x in fcm_tokens])


async def call_firebase_api(oauth_token: str, fcm_token: str, data: dict) -> (int, str):
    url = f"https://fcm.googleapis.com/v1/projects/{get_project_id()}/messages:send"

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
