import unittest
from unittest.mock import patch, AsyncMock
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

    @patch("app.main.db")
    @patch("app.main.push_call_alert", new_callable=AsyncMock)
    def test_alert_client_on_call_success(self, mock_push_call_alert, mock_db):
        mock_db.user_exits.return_value = True
        mock_push_call_alert.return_value = {"status": "sent"}
        payload = {
            "username": "sip_user",
            "phone_number": "+1234567890",
            "type": None
        }

        response = client.post("/sip/alert/call", json=payload)
        mock_db.user_exits.assert_called_once_with("sip_user")
        mock_push_call_alert.assert_awaited_once_with("sip_user", "+1234567890", payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "sent"})

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

    @patch("app.main.db")
    @patch("app.main.push_sms_alert", new_callable=AsyncMock)
    def test_alert_client_on_sms_success(self, mock_push_sms_alert, mock_db):
        mock_db.user_exits.return_value = True
        mock_push_sms_alert.return_value = {"status": "sent"}
        payload = {
            "username": "sip_user",
            "phone_number": "+1234567890",
            "body": "Hello!"
        }

        response = client.post("/sip/alert/sms", json=payload)
        mock_db.user_exits.assert_called_once_with("sip_user")
        mock_push_sms_alert.assert_awaited_once_with("sip_user", "+1234567890", "Hello!", None)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "sent"})

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

if __name__ == "__main__":
    unittest.main()
