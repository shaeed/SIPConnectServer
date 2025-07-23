from app.asterisk_config_generator import get_dongle_id
from app.services.asterisk import send_sms

async def send_gsm_sms(phone_number: str, message: str, user_name: str) -> str:
    dongle_id = get_dongle_id(user_name)
    return await send_sms(phone_number, message, dongle_id)
