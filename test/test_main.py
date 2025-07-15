import unittest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestMain(unittest.TestCase):
    def test_home(self):
        response = client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "Running"})

    @patch("app.main.add_or_update_device")
    def test_register_device(self, mock_add_or_update):
        payload = {
            "device_id": "abc123",
            "fcm_token": "token_xyz",
            "user_name": "sip_user",
            "user_pass": "secret"
        }

        response = client.post("/sip/client/register", json=payload)

        mock_add_or_update.assert_called_once_with(payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "success"})

    @patch("app.main.user_exits")
    @patch("app.main.push_call_alert", new_callable=AsyncMock)
    def test_alert_client_on_call_success(self, mock_push_call_alert, mock_user_exits):
        mock_user_exits.return_value = True
        mock_push_call_alert.return_value = {"status": "sent"}
        payload = {
            "sip_user": "sip_user",
            "phone_number": "+1234567890",
            "type": None
        }

        response = client.post("/sip/alert/call", json=payload)
        mock_user_exits.assert_called_once_with("sip_user")
        mock_push_call_alert.assert_awaited_once_with("sip_user", "+1234567890", payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "sent"})

    @patch("app.main.user_exits")
    def test_alert_client_on_call_user_not_found(self, mock_user_exits):
        mock_user_exits.return_value = False
        payload = {
            "sip_user": "sip_user",
            "phone_number": "+1234567890",
            "type": None
        }

        response = client.post("/sip/alert/call", json=payload)
        mock_user_exits.assert_called_once_with("sip_user")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "User not found"})

    @patch("app.main.user_exits")
    @patch("app.main.push_sms_alert", new_callable=AsyncMock)
    def test_alert_client_on_sms_success(self, mock_push_sms_alert, mock_user_exits):
        mock_user_exits.return_value = True
        mock_push_sms_alert.return_value = {"status": "sent"}
        payload = {
            "sip_user": "sip_user",
            "phone_number": "+1234567890",
            "body": "Hello!"
        }

        response = client.post("/sip/alert/sms", json=payload)
        mock_user_exits.assert_called_once_with("sip_user")
        mock_push_sms_alert.assert_awaited_once_with("sip_user", "+1234567890", "Hello!")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "sent"})

    @patch("app.main.user_exits")
    def test_alert_client_on_sms_user_not_found(self, mock_user_exits):
        mock_user_exits.return_value = False
        payload = {
            "sip_user": "sip_user",
            "phone_number": "+1234567890",
            "body": "Hello!"
        }

        response = client.post("/sip/alert/sms", json=payload)
        mock_user_exits.assert_called_once_with("sip_user")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "User not found"})

if __name__ == "__main__":
    unittest.main()
