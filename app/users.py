import asyncio
import traceback

from app.asterisk_config_generator import generate_configs, restart_asterisk
from app.database import get_all_users, add_or_update_user
from app.models import User


async def add_user(user: User):
    user_db_dict = {
        "user_name": user.username,
        "user_pass": user.password,
        "dongle_audio_interface": user.audio_interface,
        "dongle_data_interface": user.data_interface
    }
    voicemail_id = user.voicemail_number
    if not voicemail_id:
        voicemail_id = generate_voicemail_number()
    user_db_dict['voicemail_id'] = voicemail_id
    add_or_update_user(user_db_dict)

    # Generate configs for user and restart asterisk
    try:
        # TODO convert below to BackgroundTasks
        message = await generate_configs()
        await asyncio.sleep(1)
        message += " " + await restart_asterisk() # must start after generate_configs() completed.
        return message
    except:
        return "Either config generation or Asterisk restart failed. Exception: " + traceback.format_exc()

def generate_voicemail_number():
    users = get_all_users()
    existing_voicemails = (x["voicemail_id"] for x in users)
    start = 100
    while start in existing_voicemails:
        start += 1
    return start
