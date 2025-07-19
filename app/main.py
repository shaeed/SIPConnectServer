from typing import Optional

from fastapi import FastAPI, HTTPException
from app.database import user_exits, update_fcm_token
from app.models import User, TokenPayload, CallPayload, SmsPayload
from app.push_alerts import push_call_alert, push_sms_alert
from app.users import add_user

app = FastAPI()

@app.post("/sip/users")
async def create_users(user: User):
    if user_exits(user.user_name):
        raise HTTPException(status_code=409, detail="User name already present.")
    message = await add_user(user)
    return {"status": "success", "message": message}

@app.post("/sip/client/register")
async def register_device(payload: TokenPayload):
    if not user_exits(payload.sip_user):
        raise HTTPException(status_code=404, detail="User not found")
    message = update_fcm_token(payload.sip_user, payload.device_id, payload.fcm_token)
    return {"status": "success", "message": message}

@app.post("/sip/alert/call")
async def alert_client_on_call(payload: CallPayload):
    if not user_exits(payload.sip_user):
        raise HTTPException(status_code=404, detail="User not found")
    return await push_call_alert(payload.sip_user, payload.phone_number, payload.__dict__)

@app.post("/sip/alert/sms")
async def alert_client_on_sms(payload: SmsPayload):
    if not user_exits(payload.sip_user):
        raise HTTPException(status_code=404, detail="User not found")
    return await push_sms_alert(payload.sip_user, payload.phone_number, payload.body)

@app.get('/')
async def home():
    return {'status': 'Running'}
