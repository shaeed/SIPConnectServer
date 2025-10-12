import glob
from typing import List

from app.Constants import Const


async def read_ttyUSB_devices() -> List[str]:
    """
    Extracts all /dev/ttyUSB* device paths from the input string.
    :returns: ['/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyUSB2']
    """
    files = glob.glob('/dev/ttyUSB*')
    files.append(Const.DUMMY_TTY)
    files.append(Const.ANDROID_TTY)

    print("Devices:", files)
    return files
