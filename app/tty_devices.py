import glob
from typing import List


async def read_ttyUSB_devices() -> List[str]:
    """
    Extracts all /dev/ttyUSB* device paths from the input string.
    :returns: ['/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyUSB2']
    """
    files = glob.glob('/dev/ttyUSB*')
    files.append('/dev/dummy')
    print("Devices:", files)
    return files
