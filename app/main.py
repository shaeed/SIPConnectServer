import json
import shutil
from pathlib import Path

import aiofiles
from fastapi import FastAPI, HTTPException, Request, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse, JSONResponse
from fastapi.templating import Jinja2Templates

import app.database as db
from app.models import User, TokenPayload, CallPayload, SmsPayload
from app.services.firebase import push_call_alert, push_sms_alert
from app.tty_devices import read_ttyUSB_devices
from app.users import add_user
from app.services import gsm


app = FastAPI()
BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# interfaces = ["/dev/ttyUSB1", "/dev/ttyUSB2", "/dev/ttyUSB3", "/dev/ttyUSB4", "/dev/ttyUSB5"]

@app.post("/sip/users")
async def create_users(user: User):
    if db.user_exits(user.username):
        raise HTTPException(status_code=409, detail="User name already present.")
    message = await add_user(user)
    return {"message": message}

@app.put("/sip/users/{username}")
async def update_user(username: str, user: User):
    if not db.user_exits(username):
        raise HTTPException(status_code=409, detail="User name not present.")
    message = await add_user(user)
    return {"message": message}

@app.delete("/sip/users/{username}")
async def delete_user(username: str):
    message = delete_user(username)
    return {"message": message}

@app.post("/sip/client/register")
async def register_device(payload: TokenPayload):
    if not db.user_exits(payload.sip_user):
        raise HTTPException(status_code=404, detail="User not found")
    message = db.update_fcm_token(payload.sip_user, payload.device_id, payload.fcm_token)
    return {"message": message}

@app.post("/sip/alert/call")
async def alert_client_on_call(payload: CallPayload):
    if not db.user_exits(payload.sip_user):
        raise HTTPException(status_code=404, detail="User not found")
    return await push_call_alert(payload.sip_user, payload.phone_number, payload.__dict__)

@app.post("/sip/alert/sms")
async def alert_client_on_sms(payload: SmsPayload):
    if not db.user_exits(payload.sip_user):
        raise HTTPException(status_code=404, detail="User not found")
    return await push_sms_alert(payload.sip_user, payload.phone_number, payload.body, payload.device_id)

@app.post("/gsm/sms")
async def send_gsm_sms(payload: SmsPayload):
    if not db.user_exits(payload.sip_user):
        raise HTTPException(status_code=404, detail="User not found")
    message = await gsm.send_gsm_sms(payload.phone_number, payload.body, payload.sip_user)
    return {"status": "success", "message": message}

# @app.get('/')
# async def home():
#     return {'status': 'Running'}

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

@app.post("/upload_sa")
async def upload_service_account_file(config_file: UploadFile = File(...)):
    # Read the uploaded file content
    contents = await config_file.read()
    upload_dir = Path("uploads")
    upload_dir.mkdir(exist_ok=True)  # create folder if not exists
    save_path = upload_dir / 'service-account.json'

    async with aiofiles.open(save_path, "wb") as f:
        await f.write(contents)
    # Update db
    sa_dc = json.loads(contents.decode())
    db.set_project_id(sa_dc["project_id"])
    db.set_service_account_file_path(save_path.as_posix())

    print(f"Config file saved to: {save_path}")
    return RedirectResponse("/", status_code=303)

@app.get("/sip/db")
async def download_db():
    db_file = db.get_db_file_path()
    if Path(db_file).exists():
        return FileResponse(db_file, media_type='application/json', filename="users_db.json")
    else:
        return JSONResponse(status_code=404, content={"message": "DB file not found."})

@app.post("/sip/db")
async def upload_db(db_file: UploadFile = File(...)):
    try:
        db_file_path = db.get_db_file_path()
        contents = await db_file.read()
        async with aiofiles.open(db_file_path, "wb") as f:
            await f.write(contents)
        db.load_data(True)
        return {"message": "Database restored successfully."}
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": f"Error: {str(e)}"})
