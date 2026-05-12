import json
import unittest
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient
import app.main as main

client = TestClient(main.app)

class TestMain(unittest.IsolatedAsyncioTestCase):

    @patch("app.main.db")
    def test_home(self, mock_db):
        mock_db.get_service_account_file_path.return_value = "test-service.json"
        mock_db.get_project_id.return_value = "test-project"
        with patch("app.main.read_ttyUSB_devices", return_value=["tty1", "tty2"]):
            response = client.get("/")
            self.assertEqual(response.status_code, 200)

    @patch("app.main.db")
    def test_register_device(self, mock_db):
        mock_db.user_exits.return_value = True
        mock_db.update_fcm_token.return_value = "mocked fun called"
        payload = {
            "device_id": "abc123",
            "fcm_token": "token_xyz",
            "username": "sip_user"
        }
        response = client.post("/sip/client/register", json=payload)

        mock_db.update_fcm_token.assert_called_once_with("sip_user", "abc123", "token_xyz")
        self.assertEqual(response.status_code, 200)
        self.assertEqual({"message": "mocked fun called"}, response.json())

    @patch("app.main.db")
    def test_get_device_token(self, mock_db):
        mock_db.get_fcm_token.return_value = 'mock_token'
        response = client.get("/sip/client/token?username=sip_user&device_id=dev")

        mock_db.get_fcm_token.assert_called_once_with("sip_user", "dev")
        self.assertEqual(response.status_code, 200)
        self.assertEqual({"fcm_token": "mock_token"}, response.json())

    @patch("app.main.sql_db")
    @patch("app.main.db")
    @patch("app.main.push_call_alert", new_callable=AsyncMock)
    def test_alert_client_on_call_success(self, mock_push_call_alert, mock_db, mock_sql_db):
        mock_db.user_exits.return_value = True
        mock_sql_db.insert_call_log.return_value = None
        mock_push_call_alert.return_value = [{"status": 200, "data": {"name": "projects/test/messages/123"}}]
        payload = {
            "username": "sip_user",
            "phone_number": "+1234567890",
            "type": None
        }

        response = client.post("/sip/alert/call", json=payload)
        mock_sql_db.insert_call_log.assert_called_once_with("sip_user", "+1234567890",
                                                            json.dumps(payload, indent=None, separators=(',', ':')))
        mock_db.user_exits.assert_called_once_with("sip_user")
        mock_push_call_alert.assert_awaited_once_with("sip_user", "+1234567890", payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [{"status": 200, "data": {"name": "projects/test/messages/123"}}])

    @patch("app.main.db")
    def test_alert_client_on_call_user_not_found(self, mock_db):
        mock_db.user_exits.return_value = False
        payload = {
            "username": "sip_user",
            "phone_number": "+1234567890",
            "type": None
        }

        response = client.post("/sip/alert/call", json=payload)
        mock_db.user_exits.assert_called_once_with("sip_user")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "User name not present."})

    @patch("app.main.sql_db")
    @patch("app.main.db")
    @patch("app.main.push_sms_alert", new_callable=AsyncMock)
    def test_alert_client_on_sms_success(self, mock_push_sms_alert, mock_db, mock_sql_db):
        mock_db.user_exits.return_value = True
        mock_sql_db.insert_sms_log.return_value = None
        mock_push_sms_alert.return_value = [{"status": 200, "data": {"name": "projects/test/messages/456"}}]
        payload = {
            "username": "sip_user",
            "phone_number": "+1234567890",
            "body": "Hello!"
        }

        response = client.post("/sip/alert/sms", json=payload)
        payload["device_id"] = None
        payload["forward_to_gsm"] = None
        mock_sql_db.insert_sms_log.assert_called_once_with("sip_user", "+1234567890", "Hello!", "alert sms",
                                                           json.dumps(payload, indent=None, separators=(',', ':')))
        mock_db.user_exits.assert_called_once_with("sip_user")
        mock_push_sms_alert.assert_awaited_once_with("sip_user", "+1234567890", "Hello!", None)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [{"status": 200, "data": {"name": "projects/test/messages/456"}}])

    @patch("app.main.db")
    def test_alert_client_on_sms_user_not_found(self, mock_db):
        mock_db.user_exits.return_value = False
        payload = {
            "username": "sip_user",
            "phone_number": "+1234567890",
            "body": "Hello!"
        }

        response = client.post("/sip/alert/sms", json=payload)
        mock_db.user_exits.assert_called_once_with("sip_user")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "User name not present."})

    # ------------------------------------------------------------------
    # GET /sip/users
    # ------------------------------------------------------------------

    @patch("app.main.db")
    def test_list_users_success(self, mock_db):
        mock_db.get_all_users.return_value = [
            {
                'username': 'alice',
                'dongle_audio_interface': '/dev/ttyUSB1',
                'dongle_data_interface': '/dev/ttyUSB2',
                'voicemail_id': '100'
            },
            {
                'username': 'bob',
                'dongle_audio_interface': '/dev/ttyUSB3',
                'dongle_data_interface': '/dev/ttyUSB4',
                'voicemail_id': None
            }
        ]
        response = client.get("/sip/users")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0], {
            'username': 'alice',
            'audio_interface': '/dev/ttyUSB1',
            'data_interface': '/dev/ttyUSB2',
            'voicemail_number': '100'
        })
        self.assertIsNone(data[1]['voicemail_number'])
        self.assertNotIn('password', data[0])

    @patch("app.main.db")
    def test_list_users_empty(self, mock_db):
        mock_db.get_all_users.return_value = []
        response = client.get("/sip/users")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    # ------------------------------------------------------------------
    # GET /sip/users/{username}
    # ------------------------------------------------------------------

    @patch("app.main.db")
    def test_get_user_success(self, mock_db):
        mock_db.get_user_data.return_value = {
            'username': 'alice',
            'dongle_audio_interface': '/dev/ttyUSB1',
            'dongle_data_interface': '/dev/ttyUSB2',
            'voicemail_id': '100'
        }
        response = client.get("/sip/users/alice")
        mock_db.get_user_data.assert_called_once_with("alice")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            'username': 'alice',
            'audio_interface': '/dev/ttyUSB1',
            'data_interface': '/dev/ttyUSB2',
            'voicemail_number': '100'
        })
        self.assertNotIn('password', response.json())

    @patch("app.main.db")
    def test_get_user_not_found(self, mock_db):
        mock_db.get_user_data.return_value = None
        response = client.get("/sip/users/nonexistent")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "User name not present."})

    # ------------------------------------------------------------------
    # GET /api/tty-devices
    # ------------------------------------------------------------------

    @patch("app.main.read_ttyUSB_devices", new_callable=AsyncMock)
    def test_get_tty_devices(self, mock_read_tty):
        mock_read_tty.return_value = ["/dev/ttyUSB0", "/dev/ttyUSB1", "/dev/dummy"]
        response = client.get("/api/tty-devices")
        mock_read_tty.assert_awaited_once()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), ["/dev/ttyUSB0", "/dev/ttyUSB1", "/dev/dummy"])

    # ------------------------------------------------------------------
    # GET /api/config
    # ------------------------------------------------------------------

    @patch("app.main.db")
    def test_get_config_configured(self, mock_db):
        mock_db.get_service_account_file_path.return_value = "uploads/service-account.json"
        mock_db.get_project_id.return_value = "my-project-123"
        response = client.get("/api/config")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"sa_configured": True, "project_id": "my-project-123"})

    @patch("app.main.db")
    def test_get_config_not_configured(self, mock_db):
        mock_db.get_service_account_file_path.return_value = "uploads/dummy-service-account.json"
        mock_db.get_project_id.return_value = "dummy-project-id"
        response = client.get("/api/config")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"sa_configured": False, "project_id": ""})

    # ------------------------------------------------------------------
    # POST /upload_sa
    # ------------------------------------------------------------------

    @patch("app.main.db")
    @patch("aiofiles.open")
    def test_upload_sa_success(self, mock_aiofiles_open, mock_db):
        mock_file = AsyncMock()
        mock_cm = MagicMock()
        mock_cm.__aenter__ = AsyncMock(return_value=mock_file)
        mock_cm.__aexit__ = AsyncMock(return_value=None)
        mock_aiofiles_open.return_value = mock_cm

        sa_content = json.dumps({"project_id": "test-project-id", "type": "service_account"})
        with patch("pathlib.Path.mkdir"):
            response = client.post(
                "/upload_sa",
                files={"config_file": ("service-account.json", sa_content.encode(), "application/json")}
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "Service account uploaded successfully."})
        mock_db.set_project_id.assert_called_once_with("test-project-id")
        mock_db.set_service_account_file_path.assert_called_once()


if __name__ == "__main__":
    unittest.main()
