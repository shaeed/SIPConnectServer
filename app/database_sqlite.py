import sqlite3
from contextlib import closing

SQLite_FILE = r'/var/log/asterisk/master.db'
DB_PATH = SQLite_FILE

async def create_sql_tables() -> str:
    conn = sqlite3.connect(SQLite_FILE)
    cursor = conn.cursor()

    # cursor.execute("""
    #     CREATE TABLE IF NOT EXISTS cdr (
    #         calldate     VARCHAR(30),
    #         clid         VARCHAR(80),
    #         src          VARCHAR(80),
    #         dst          VARCHAR(80),
    #         dcontext     VARCHAR(80),
    #         channel      VARCHAR(80),
    #         dstchannel   VARCHAR(80),
    #         lastapp      VARCHAR(80),
    #         lastdata     VARCHAR(80),
    #         duration     INTEGER,
    #         billsec      INTEGER,
    #         disposition  VARCHAR(45),
    #         amaflags     INTEGER,
    #         accountcode  VARCHAR(20),
    #         uniqueid     VARCHAR(32),
    #         userfield    VARCHAR(255)
    #     );
    # """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sms_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            user TEXT,
            number TEXT,
            message TEXT
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fastapi_call_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT,
            number TEXT,
            payload_json TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fastapi_sms_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            user TEXT,
            number TEXT,
            message TEXT,
            sms_type TEXT,
            payload_json TEXT
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()
    return f"CDR & sms_log table created (or already exists) in {SQLite_FILE}"

def insert_call_log(username: str, phone_number: str, payload_json: str):
    try:
        with closing(sqlite3.connect(DB_PATH)) as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO fastapi_call_log (user, number, payload_json)
                VALUES (?, ?, ?)
            """, (username, phone_number, payload_json))
            conn.commit()
    except Exception as e:
        print("Exception in DB operation", e)

def insert_sms_log(username: str, phone_number: str, body: str, sms_type: str, payload_json: str):
    try:
        with closing(sqlite3.connect(DB_PATH)) as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO fastapi_sms_log (user, number, message, sms_type, payload_json)
                VALUES (?, ?, ?, ?, ?)
            """, (username, phone_number, body, sms_type, payload_json))
            conn.commit()
    except Exception as e:
        print("Exception in DB operation", e)

def get_sms_logs():
    """Return SMS logs as JSON."""
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cursor = conn.cursor()
        cursor.execute("""
                SELECT id, user, number, message, sms_type, timestamp
                FROM fastapi_sms_log
                ORDER BY timestamp DESC
            """)
        sms_logs = cursor.fetchall()
    return sms_logs

def get_call_logs():
    """Return call logs as JSON."""
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cursor = conn.cursor()
        cursor.execute("""
                SELECT id, user, number, timestamp
                FROM fastapi_call_log
                ORDER BY timestamp DESC
            """)
        call_logs = cursor.fetchall()
    return call_logs
