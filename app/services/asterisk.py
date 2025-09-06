import asyncio
import re
import sqlite3
import traceback

import aiofiles

from app.asterisk_config_generator import generate_configs, update_file

RTP_FILE = r'/etc/asterisk/rtp.conf'
SQLite_CONFIG_FILE = r'/etc/asterisk/cdr_sqlite3_custom.conf'
SQLite_FILE = r'/var/log/asterisk/master.db'


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

async def configure_asterisk() -> str:
    """
    Generate configs for user and restart asterisk
    :return: Generation message
    """
    # TODO convert below to BackgroundTasks
    try:
        await first_time_init()
        message = await generate_configs()
        await asyncio.sleep(1)
        message += " " + await restart_asterisk()  # must start after generate_configs() completed.
        return message
    except Exception:
        return "Either config generation or Asterisk restart failed. Exception: " + traceback.format_exc()

async def first_time_init():
    await update_rtp_ports(10000, 10060, RTP_FILE)
    await enable_sqlite_cdr(SQLite_CONFIG_FILE)
    await create_sql_tables(SQLite_FILE)

async def update_rtp_ports(start: int, end: int, rtp_file: str):
    async with aiofiles.open(rtp_file, 'r') as file:
        file_content = await file.read()
    file_content = re.sub(r'\nrtpstart=\s*\d+', f'\nrtpstart={start}', file_content)
    file_content = re.sub(r'\nrtpend=\s*\d+', f'\nrtpend={end}', file_content)

    await update_file('', [file_content], rtp_file, True)

async def enable_sqlite_cdr(file_path: str):
    config = """
[master] ; currently, only file "master.db" is supported, with only one table at a time.
table => cdr
columns => calldate, clid, dcontext, channel, dstchannel, lastapp, lastdata, duration, billsec, disposition, amaflags, accountcode, uniqueid, userfield, test
values => '${CDR(start)}','${CDR(clid)}','${CDR(dcontext)}','${CDR(channel)}','${CDR(dstchannel)}','${CDR(lastapp)}','${CDR(lastdata)}','${CDR(duration)}','${CDR(billsec)}','${CDR(disposition)}','${CDR(amaflags)}','${CDR(accountcode)}','${CDR(uniqueid)}','${CDR(userfield)}','${CDR(test)}'
busy_timeout => 1000

    """
    await update_file('', [config], file_path, True)

async def create_sql_tables(db_path: str) -> str:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cdr (
            calldate     VARCHAR(30),
            clid         VARCHAR(80),
            src          VARCHAR(80),
            dst          VARCHAR(80),
            dcontext     VARCHAR(80),
            channel      VARCHAR(80),
            dstchannel   VARCHAR(80),
            lastapp      VARCHAR(80),
            lastdata     VARCHAR(80),
            duration     INTEGER,
            billsec      INTEGER,
            disposition  VARCHAR(45),
            amaflags     INTEGER,
            accountcode  VARCHAR(20),
            uniqueid     VARCHAR(32),
            userfield    VARCHAR(255)
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sms_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            received_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            user TEXT,
            number TEXT,
            message TEXT
        );
    """)

    conn.commit()
    cursor.close()
    conn.close()
    return f"CDR & sms_log table created (or already exists) in {db_path}"
