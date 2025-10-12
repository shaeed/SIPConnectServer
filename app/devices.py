from app.Constants import Const
from app.database import get_user_data


def determine_outgoing_system(username: str) -> str:
    user_data = get_user_data(username)
    if user_data.get('dongle_data_interface') == Const.DUMMY_TTY:
        return Const.DEV_DUMMY
    if user_data.get('dongle_data_interface') == Const.ANDROID_TTY:
        return Const.DEV_ANDROID
    return Const.DEV_DONGLE_HUAWEI

