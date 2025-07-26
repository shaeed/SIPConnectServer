
import unittest
from unittest.mock import patch, AsyncMock, call, MagicMock
from app.services.firebase import push_call_alert, push_sms_alert, call_firebase_api

class TestPushAlerts(unittest.IsolatedAsyncioTestCase):

    @patch("app.services.firebase.get_fcm_tokens")
    @patch("app.services.firebase.get_oauth_token")
    @patch("app.services.firebase.call_firebase_api", new_callable=AsyncMock)
    async def test_push_call_alert_normal_call(self, mock_call_firebase_api, mock_get_oauth_token, mock_get_fcm_tokens):
        mock_get_fcm_tokens.return_value = ["mock_fcm_token"]
        mock_get_oauth_token.return_value = "mock_oauth_token"
        mock_call_firebase_api.return_value = {"status": "success"}

        result = await push_call_alert("sip_user1", "+1234567890")
        mock_get_fcm_tokens.assert_called_once_with("sip_user1")
        mock_get_oauth_token.assert_called_once_with("sip_user1")
        mock_call_firebase_api.assert_awaited_once_with(
            "mock_oauth_token",
            "mock_fcm_token",
            {"type": "call", "phone_number": "+1234567890"}
        )
        self.assertEqual(result, [{"status": "success"}])

    @patch("app.services.firebase.get_fcm_tokens")
    @patch("app.services.firebase.get_oauth_token")
    @patch("app.services.firebase.call_firebase_api", new_callable=AsyncMock)
    async def test_push_call_alert_normal_call_2_device(self, mock_call_firebase_api, mock_get_oauth_token, mock_get_fcm_tokens):
        mock_get_fcm_tokens.return_value = ["mock_fcm_token1", "mock_fcm_token2"]
        mock_get_oauth_token.return_value = "mock_oauth_token"
        mock_call_firebase_api.return_value = {"status": "success"}

        result = await push_call_alert("sip_user1", "+1234567890")
        mock_get_fcm_tokens.assert_called_once_with("sip_user1")
        mock_get_oauth_token.assert_called_once_with("sip_user1")
        mock_call_firebase_api.assert_has_awaits([
            call("mock_oauth_token", "mock_fcm_token1", {"type": "call", "phone_number": "+1234567890"}),
            call("mock_oauth_token", "mock_fcm_token2", {"type": "call", "phone_number": "+1234567890"})
        ])
        self.assertEqual(mock_call_firebase_api.await_count, 2)
        self.assertEqual(result, [{"status": "success"}, {"status": "success"}])

    @patch("app.services.firebase.get_fcm_tokens")
    @patch("app.services.firebase.get_oauth_token")
    @patch("app.services.firebase.call_firebase_api", new_callable=AsyncMock)
    async def test_push_call_alert_missed_call(self, mock_call_firebase_api, mock_get_oauth_token, mock_get_fcm_tokens):
        # Arrange
        mock_get_fcm_tokens.return_value = ["mock_fcm_token"]
        mock_get_oauth_token.return_value = "mock_oauth_token"
        mock_call_firebase_api.return_value = {"status": "success"}
        payload = {"type": "missed"}

        result = await push_call_alert("sip_user2", "+0987654321", payload)
        mock_call_firebase_api.assert_awaited_once_with(
            "mock_oauth_token",
            "mock_fcm_token",
            {"type": "missed-call", "phone_number": "+0987654321"}
        )
        self.assertEqual(result, [{"status": "success"}])

    @patch("app.services.firebase.get_fcm_tokens")
    @patch("app.services.firebase.get_oauth_token")
    @patch("app.services.firebase.call_firebase_api", new_callable=AsyncMock)
    async def test_push_sms_alert(self, mock_call_firebase_api, mock_get_oauth_token, mock_get_fcm_tokens):
        mock_get_fcm_tokens.return_value = ["mock_fcm_token"]
        mock_get_oauth_token.return_value = "mock_oauth_token"
        mock_call_firebase_api.return_value = {"status": "success"}
        sip_user = "sip_user1"
        phone_number = "+1234567890"
        message_body = "Hello, this is a test SMS."

        result = await push_sms_alert(sip_user, phone_number, message_body)
        mock_get_fcm_tokens.assert_called_once_with(sip_user)
        mock_get_oauth_token.assert_called_once_with(sip_user)
        mock_call_firebase_api.assert_awaited_once_with(
            "mock_oauth_token",
            "mock_fcm_token",
            {
                "type": "sms",
                "phone_number": phone_number,
                "body": message_body
            }
        )
        self.assertEqual(result, [{"status": "success"}])

    @patch("app.services.firebase.get_fcm_tokens_with_device_id")
    @patch("app.services.firebase.get_oauth_token")
    @patch("app.services.firebase.call_firebase_api", new_callable=AsyncMock)
    async def test_push_sms_alert_filter_fcm(self, mock_call_firebase_api, mock_get_oauth_token, mock_get_fcm_tokens_with_device_id):
        mock_get_fcm_tokens_with_device_id.return_value = {"dev1": "mock_fcm_token", "dev2": "mock_fcm_token2"}
        mock_get_oauth_token.return_value = "mock_oauth_token"
        mock_call_firebase_api.return_value = {"status": "success"}
        sip_user = "sip_user1"
        phone_number = "+1234567890"
        message_body = "Hello, this is a test SMS."

        result = await push_sms_alert(sip_user, phone_number, message_body, "dev2")
        mock_get_fcm_tokens_with_device_id.assert_called_once_with(sip_user)
        mock_get_oauth_token.assert_called_once_with(sip_user)
        mock_call_firebase_api.assert_awaited_once_with(
            "mock_oauth_token",
            "mock_fcm_token",
            {
                "type": "sms",
                "phone_number": phone_number,
                "body": message_body
            }
        )
        self.assertEqual(result, [{"status": "success"}])

    @patch("app.services.firebase.aiohttp.ClientSession")
    @patch("app.services.firebase.get_project_id")
    async def test_call_firebase_api_success(self, mock_get_project_id, mock_client_session):
        mock_get_project_id.return_value = "test-project"
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"name": "fake-message-id"})
        # make response object as Context aware
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)

        mock_session_context = MagicMock()
        mock_session_context.__aenter__ = AsyncMock(return_value=mock_session_context)
        mock_session_context.post = MagicMock(return_value=mock_response)

        mock_client_session.return_value = mock_session_context

        oauth_token = "mock_oauth"
        fcm_token = "mock_fcm"
        data = {"type": "sms", "phone_number": "+1234567890", "body": "Hello!"}

        result = await call_firebase_api(oauth_token, fcm_token, data)

        mock_client_session.assert_called_once()
        mock_session_context.__aenter__.return_value.post.assert_called_once()
        args, kwargs = mock_session_context.__aenter__.return_value.post.call_args

        url = args[0]
        self.assertIn("https://fcm.googleapis.com/v1/projects/", url)

        self.assertEqual(kwargs["json"], {
            "message": {
                "token": fcm_token,
                "android": {"priority": "high"},
                "data": data
            }
        })

        self.assertEqual(kwargs["headers"], {
            "Authorization": f"Bearer {oauth_token}",
            "Content-Type": "application/json; UTF-8"
        })

        self.assertEqual(result, {
            "status": 200,
            "data": {"name": "fake-message-id"}
        })


if __name__ == '__main__':
    unittest.main()
