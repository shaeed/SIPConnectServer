
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from database import add_or_update_device, user_exits
from push_alerts import push_call_alert, push_sms_alert

app = FastAPI()

class TokenPayload(BaseModel):
    device_id: str
    fcm_token: str
    user_name: str
    user_pass: str

class CallPayload(BaseModel):
    sip_user: str
    phone_number: str

class SmsPayload(BaseModel):
    sip_user: str
    phone_number: str
    body: str

@app.post("/sip/client/register")
async def register_device(payload: TokenPayload):
    if payload.fcm_token:
        add_or_update_device(payload.__dict__)
    return {"status": "success"}

@app.post("/sip/alert/call")
async def alert_client_on_call(payload: CallPayload):
    if not user_exits(payload.sip_user):
        raise HTTPException(status_code=404, detail="User not found")
    return await push_call_alert(payload.sip_user, payload.phone_number)

@app.post("/sip/alert/sms")
async def alert_client_on_sms(payload: SmsPayload):
    if not user_exits(payload.sip_user):
        raise HTTPException(status_code=404, detail="User not found")
    return await push_sms_alert(payload.sip_user, payload.phone_number, payload.body)

@app.get('/')
async def home():
    return {'status': 'Running'}
