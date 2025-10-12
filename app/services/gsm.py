from fastapi import HTTPException

from app.Constants import Const
from app.asterisk_config_generator import get_dongle_id
from app.devices import determine_outgoing_system
from app.services.asterisk import send_sms
from app.services.firebase import push_sms_alert


async def send_gsm_sms(phone_number: str, message: str, username: str, device_id: str):
    if determine_outgoing_system(username) == Const.DEV_DONGLE_HUAWEI:
        dongle_id = get_dongle_id(username)
        try:
            return await send_sms(phone_number, message, dongle_id)
        except Exception as e:
            print(f'Failed to send message. Exception: {str(e)}')
            raise HTTPException(status_code=500, detail=f"Failed to send message. {str(e)}")
    else:
        return await push_sms_alert(username, phone_number, message, device_id, True)
