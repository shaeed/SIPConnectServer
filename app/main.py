import json
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.database import user_exits, update_fcm_token, get_all_users, set_project_id, set_service_account_file_path, \
    get_service_account_file_path, get_project_id
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
    if user_exits(user.username):
        raise HTTPException(status_code=409, detail="User name already present.")
    message = await add_user(user)
    return {"status": "success", "message": message}

@app.put("/sip/users/{username}")
async def update_user(username: str, user: User):
    if not user_exits(username):
        raise HTTPException(status_code=409, detail="User name not present.")
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

@app.post("/gsm/sms")
async def send_gsm_sms(payload: SmsPayload):
    if not user_exits(payload.sip_user):
        raise HTTPException(status_code=404, detail="User not found")
    message = await gsm.send_gsm_sms(payload.phone_number, payload.body, payload.sip_user)
    return {"status": "success", "message": message}

# @app.get('/')
# async def home():
#     return {'status': 'Running'}

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    global templates
    users = get_all_users()
    sa_file = get_service_account_file_path()
    sa_status = f'[Valid file already uploaded]' if 'dummy' not in sa_file else ''
    project_id = get_project_id()
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

    with open(save_path, "wb") as f:
        f.write(contents)
    # Update db
    sa_dc = json.loads(contents.decode())
    set_project_id(sa_dc["project_id"])
    set_service_account_file_path(save_path.as_posix())

    print(f"Config file saved to: {save_path}")
    return RedirectResponse("/", status_code=303)
