import json
from pathlib import Path
from typing import List

import aiofiles
from fastapi import FastAPI, HTTPException, Request, UploadFile, File, Query
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates

import app.database as db
import app.database_sqlite as sql_db
from app.models import (User, TokenPayload, CallPayload, SmsPayload, RestartPayload,
                        MessageResponse, DeviceResponse, FirebaseResponse,
                        SmsLogEntry, CallLogEntry, SmsLogsResponse, CallLogsResponse,
                        UserResponse, ConfigResponse)
from app.services.asterisk import restart_asterisk, configure_asterisk
from app.services.firebase import push_call_alert, push_sms_alert
from app.tty_devices import read_ttyUSB_devices
from app.users import add_user
from app.services import gsm


app = FastAPI()
BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# interfaces = ["/dev/ttyUSB1", "/dev/ttyUSB2", "/dev/ttyUSB3", "/dev/ttyUSB4", "/dev/ttyUSB5"]

@app.get("/sip/users", response_model=List[UserResponse])
async def list_users():
    users = db.get_all_users()
    return [UserResponse(
        username=u['username'],
        audio_interface=u['dongle_audio_interface'],
        data_interface=u['dongle_data_interface'],
        voicemail_number=str(u['voicemail_id']) if u.get('voicemail_id') else None
    ) for u in users]

@app.get("/sip/users/{username}", response_model=UserResponse)
async def get_user(username: str):
    user = db.get_user_data(username)
    if not user:
        raise HTTPException(status_code=404, detail="User name not present.")
    return UserResponse(
        username=user['username'],
        audio_interface=user['dongle_audio_interface'],
        data_interface=user['dongle_data_interface'],
        voicemail_number=str(user['voicemail_id']) if user.get('voicemail_id') else None
    )

@app.get("/api/config", response_model=ConfigResponse)
async def get_config():
    sa_file = db.get_service_account_file_path()
    project_id = db.get_project_id()
    return ConfigResponse(
        sa_configured='dummy' not in sa_file,
        project_id='' if project_id == 'dummy-project-id' else project_id
    )

@app.post("/sip/users", response_model=MessageResponse)
async def create_user(user: User):
    if db.user_exits(user.username):
        raise HTTPException(status_code=409, detail="User name already present.")
    message = await add_user(user)
    return MessageResponse(message=message)

@app.put("/sip/users/{username}", response_model=MessageResponse)
async def update_user(username: str, user: User):
    if not db.user_exits(username):
        raise HTTPException(status_code=404, detail="User name not present.")
    message = await add_user(user)
    return MessageResponse(message=message)

@app.delete("/sip/users/{username}", response_model=MessageResponse)
async def delete_user(username: str):
    if not db.user_exits(username):
        raise HTTPException(status_code=404, detail="User name not present.")
    message = db.delete_user(username)
    return MessageResponse(message=message)

@app.post("/sip/client/register", response_model=MessageResponse)
async def register_device(payload: TokenPayload):
    if not db.user_exits(payload.username):
        raise HTTPException(status_code=404, detail="User name not present.")
    message = db.update_fcm_token(payload.username, payload.device_id, payload.fcm_token)
    return MessageResponse(message=message)

@app.get("/sip/client/token", response_model=DeviceResponse)
async def get_device_token(username: str = Query(..., description="The username (sip user name)."),
                                  device_id: str = Query(..., description="The device ID")):
    token = db.get_fcm_token(username, device_id) or ""
    return DeviceResponse(fcm_token=token)

@app.post("/sip/alert/call", response_model=List[FirebaseResponse])
async def alert_client_on_call(payload: CallPayload):
    if not db.user_exits(payload.username):
        raise HTTPException(status_code=404, detail="User name not present.")
    sql_db.insert_call_log(payload.username, payload.phone_number, payload.model_dump_json())
    return await push_call_alert(payload.username, payload.phone_number, payload.__dict__)

@app.post("/sip/alert/sms", response_model=List[FirebaseResponse])
async def alert_client_on_sms(payload: SmsPayload):
    if not db.user_exits(payload.username):
        raise HTTPException(status_code=404, detail="User name not present.")
    sql_db.insert_sms_log(
        payload.username, payload.phone_number, payload.body, "alert sms", payload.model_dump_json())
    return await push_sms_alert(payload.username, payload.phone_number, payload.body, payload.device_id)

@app.post("/gsm/sms", response_model=MessageResponse)
async def send_gsm_sms(payload: SmsPayload):
    if not db.user_exits(payload.username):
        raise HTTPException(status_code=404, detail="User name not present.")
    sql_db.insert_sms_log(
        payload.username, payload.phone_number, payload.body, "gsm sms", payload.model_dump_json())
    result = await gsm.send_gsm_sms(payload.phone_number, payload.body, payload.username, payload.device_id)
    if isinstance(result, str):
        return MessageResponse(message=result)
    return MessageResponse(message=f"SMS forwarded via GSM/Firebase to {len(result)} device(s).")

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    users = db.get_all_users()
    sa_file = db.get_service_account_file_path()
    sa_status = f'[Valid file already uploaded]' if 'dummy' not in sa_file else ''
    project_id = db.get_project_id()
    project_id = '' if 'dummy-project-id' == project_id else project_id

    interfaces = await read_ttyUSB_devices()

    return templates.TemplateResponse(request, "dashboard.html", {
        "request": request,
        "audio_interfaces": interfaces,
        "data_interfaces": interfaces,
        "users": users,
        "sa_status": sa_status,
        "project_id": project_id
    })

@app.get("/logs", response_class=HTMLResponse)
async def logs_page(request: Request):
    """Render the logs page (empty table; data loaded via AJAX)."""
    return templates.TemplateResponse("logs.html", {"request": request})

@app.get("/api/logs/sms", response_model=SmsLogsResponse)
async def get_sms_logs():
    sms_logs = sql_db.get_sms_logs()
    return SmsLogsResponse(data=[
        SmsLogEntry(id=log[0], user=log[1], number=log[2], message=log[3], sms_type=log[4], timestamp=log[5])
        for log in sms_logs
    ])

@app.get("/api/logs/call", response_model=CallLogsResponse)
async def get_call_logs():
    call_logs = sql_db.get_call_logs()
    return CallLogsResponse(data=[
        CallLogEntry(id=log[0], user=log[1], number=log[2], timestamp=log[3])
        for log in call_logs
    ])

@app.post("/upload_sa", response_model=MessageResponse)
async def upload_service_account_file(config_file: UploadFile = File(...)):
    contents = await config_file.read()
    upload_dir = Path("uploads")
    upload_dir.mkdir(exist_ok=True)
    save_path = upload_dir / 'service-account.json'

    async with aiofiles.open(save_path, "wb") as f:
        await f.write(contents)
    sa_dc = json.loads(contents.decode())
    db.set_project_id(sa_dc["project_id"])
    db.set_service_account_file_path(save_path.as_posix())
    return MessageResponse(message="Service account uploaded successfully.")

@app.get("/sip/db")
async def download_db():
    db_file = db.get_db_file_path()
    if Path(db_file).exists():
        return FileResponse(db_file, media_type='application/json', filename="users_db.json")
    raise HTTPException(status_code=404, detail="DB file not found.")

@app.post("/sip/db", response_model=MessageResponse)
async def upload_db(db_file: UploadFile = File(...)):
    try:
        db_file_path = db.get_db_file_path()
        contents = await db_file.read()
        async with aiofiles.open(db_file_path, "wb") as f:
            await f.write(contents)
        db.load_data(True)
        message = await configure_asterisk()
        return MessageResponse(message="Database restored successfully. " + message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post("/sip/restart", response_model=MessageResponse)
async def restart_sip_server(payload: RestartPayload):
    if not db.user_exits(payload.username):
        raise HTTPException(status_code=404, detail="User name not present.")
    message = await restart_asterisk()
    return MessageResponse(message=message)
