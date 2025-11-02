import tempfile
import unittest
import sqlite3
import asyncio

import app.database_sqlite
from app.database_sqlite import create_sql_tables, insert_call_log, insert_sms_log


class TestDatabaseFunctions(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Create in-memory tables before tests."""
        app.database_sqlite.SQLite_FILE = tempfile.NamedTemporaryFile(suffix=".db").name
        app.database_sqlite.DB_PATH = app.database_sqlite.SQLite_FILE
        asyncio.run(create_sql_tables())

    def setUp(self):
        """Connect fresh before each test."""
        self.conn = sqlite3.connect(app.database_sqlite.DB_PATH)
        self.cur = self.conn.cursor()

    def tearDown(self):
        self.conn.close()

    def test_tables_created(self):
        """Ensure tables exist after initialization."""
        tables = [r[0] for r in self.cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        self.assertIn("fastapi_call_log", tables)
        self.assertIn("fastapi_sms_log", tables)
        self.assertIn("sms_log", tables)

    def test_insert_call_log(self):
        """Test inserting into fastapi_call_log table."""
        insert_call_log("user1", "+91123456789", '{"test": "data"}')
        result = self.cur.execute("SELECT user, number, payload_json FROM fastapi_call_log").fetchone()
        self.assertEqual(result[0], "user1")
        self.assertEqual(result[1], "+91123456789")
        self.assertEqual(result[2], '{"test": "data"}')

    def test_insert_sms_log(self):
        """Test inserting into fastapi_sms_log table."""
        insert_sms_log("user2", "+91987654321", "Hello", "incoming", '{"key": "val"}')
        result = self.cur.execute(
            "SELECT user, number, message, sms_type, payload_json FROM fastapi_sms_log").fetchone()
        self.assertEqual(result[0], "user2")
        self.assertEqual(result[1], "+91987654321")
        self.assertEqual(result[2], "Hello")
        self.assertEqual(result[3], "incoming")
        self.assertEqual(result[4], '{"key": "val"}')

    def test_multiple_inserts(self):
        """Ensure multiple inserts work correctly."""
        insert_call_log("multi1", "123", '{"a":1}')
        insert_call_log("multi2", "456", '{"b":2}')
        count = self.cur.execute("SELECT COUNT(*) FROM fastapi_call_log").fetchone()[0]
        self.assertGreaterEqual(count, 2)


if __name__ == "__main__":
    unittest.main()
