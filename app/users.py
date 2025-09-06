from app.database import get_all_users, add_or_update_user
from app.models import User
from app.services.asterisk import configure_asterisk


async def add_user(user: User):
    user_db_dict = {
        "username": user.username,
        "user_pass": user.password,
        "dongle_audio_interface": user.audio_interface,
        "dongle_data_interface": user.data_interface
    }
    voicemail_id = user.voicemail_number
    if not voicemail_id:
        voicemail_id = generate_voicemail_number()
    user_db_dict['voicemail_id'] = voicemail_id
    add_or_update_user(user_db_dict)
    return await configure_asterisk()

def generate_voicemail_number():
    users = get_all_users()
    existing_voicemails = (x["voicemail_id"] for x in users)
    start = 100
    while start in existing_voicemails:
        start += 1
    return start
