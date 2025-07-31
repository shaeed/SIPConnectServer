from app.asterisk_config_generator import get_dongle_id
from app.services.asterisk import send_sms

async def send_gsm_sms(phone_number: str, message: str, username: str) -> str:
    dongle_id = get_dongle_id(username)
    return await send_sms(phone_number, message, dongle_id)
