import asyncio

async def send_sms(phone_number: str, message: str, dongle_id: str) -> str:
    command = f'dongle sms {dongle_id} {phone_number} {message}'
    return_code, log = await run_in_asterisk(command)
    if return_code == 0:
        return "Message scheduled to be sent."
    else:
        return f"Asterisk error. Return code: {return_code}. Log: {log}"

async def restart_asterisk() -> str:
    command = 'core restart now'
    return_code, log = await run_in_asterisk(command)
    if return_code == 0:
        return "Asterisk restarted successfully."
    else:
        return f"Asterisk failed to restart. Return code: {return_code}. Log: {log}"

async def run_in_asterisk(command: str) -> (int, str):
    process = await asyncio.create_subprocess_exec(
        'asterisk', '-rx', command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()

    # log = f'[stdout]\n{stdout.decode()}'
    log = f'[stderr]\n{stderr.decode()}'
    return_code = process.returncode
    return return_code, log
