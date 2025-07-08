
import aiohttp
import asyncio
from database import get_fcm_token, add_dummy_user, delete_device
from oAuth2_generator import PROJECT_ID, get_oauth_token

async def push_call_alert(sip_user: str, phone_number: str):
    fcm_token = get_fcm_token(sip_user)
    oauth_token = get_oauth_token(sip_user)
    data = {"type": "call", "phone_number": phone_number}
    return await call_firebase_api(oauth_token, fcm_token, data)

async def push_sms_alert(sip_user: str, phone_number: str, message_body: str):
    fcm_token = get_fcm_token(sip_user)
    oauth_token = get_oauth_token(sip_user)
    data = {"type": "sms", "phone_number": phone_number, "body": message_body}
    return await call_firebase_api(oauth_token, fcm_token, data)


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

# Few test case
if __name__ == '__main__':
    async def main():
        add_dummy_user()
        await asyncio.gather(
            push_call_alert('dummy_user', '+919912345678'),
            push_sms_alert('dummy_user', '+919912345678', 'sample message')
        )
        delete_device('dummy_user')
    asyncio.run(main())
