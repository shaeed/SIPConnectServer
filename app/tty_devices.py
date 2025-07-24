
import re

import asyncio
from typing import List


async def read_ttyUSB_devices() -> List[str]:
    """
    Extracts all /dev/ttyUSB* device paths from the input string.
    :returns: ['/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyUSB2']
    """
    process = await asyncio.create_subprocess_exec(
        'ls', '-l', '/dev/ttyUSB*',
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    stdout = stdout.decode()

    pattern = r'/dev/ttyUSB\d+'
    devices = re.findall(pattern, stdout)
    print(stdout)
    print("Devices:", devices)
    return devices
