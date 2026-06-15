
import unittest
from unittest.mock import patch, AsyncMock, MagicMock

from pywebpush import WebPushException
from app.services.webpush import push_web_call_alert, push_web_sms_alert, send_web_push

VAPID_KEYS = {"private_key": "mock_private_key", "public_key": "mock_public_key", "subject": "mailto:admin@example.com"}

class TestPushWebAlerts(unittest.IsolatedAsyncioTestCase):

    @patch("app.services.webpush.get_web_subscriptions_with_device_id")
    @patch("app.services.webpush.send_web_push", new_callable=AsyncMock)
    async def test_push_web_call_alert_normal_call(self, mock_send_web_push, mock_get_subscriptions):
        mock_get_subscriptions.return_value = {"dev1": {"endpoint": "https://push.example.com/1"}}
        mock_send_web_push.return_value = {"status": 201, "data": {"message": "Push sent"}}

        result = await push_web_call_alert("sip_user1", "+1234567890")

        mock_get_subscriptions.assert_called_once_with("sip_user1")
        mock_send_web_push.assert_awaited_once_with(
            "sip_user1", "dev1", {"endpoint": "https://push.example.com/1"},
            "Incoming Call", "+1234567890", {"type": "call", "phone_number": "+1234567890"}
        )
        self.assertEqual(result, [{"status": 201, "data": {"message": "Push sent"}}])

    @patch("app.services.webpush.get_web_subscriptions_with_device_id")
    @patch("app.services.webpush.send_web_push", new_callable=AsyncMock)
    async def test_push_web_call_alert_missed_call(self, mock_send_web_push, mock_get_subscriptions):
        mock_get_subscriptions.return_value = {"dev1": {"endpoint": "https://push.example.com/1"}}
        mock_send_web_push.return_value = {"status": 201, "data": {"message": "Push sent"}}

        result = await push_web_call_alert("sip_user1", "+1234567890", {"type": "missed"})

        mock_send_web_push.assert_awaited_once_with(
            "sip_user1", "dev1", {"endpoint": "https://push.example.com/1"},
            "Missed Call", "+1234567890", {"type": "missed-call", "phone_number": "+1234567890"}
        )
        self.assertEqual(result, [{"status": 201, "data": {"message": "Push sent"}}])

    @patch("app.services.webpush.get_web_subscriptions_with_device_id")
    @patch("app.services.webpush.send_web_push", new_callable=AsyncMock)
    async def test_push_web_sms_alert(self, mock_send_web_push, mock_get_subscriptions):
        mock_get_subscriptions.return_value = {"dev1": {"endpoint": "https://push.example.com/1"}}
        mock_send_web_push.return_value = {"status": 201, "data": {"message": "Push sent"}}

        result = await push_web_sms_alert("sip_user1", "+1234567890", "Hello, this is a test SMS.")

        mock_send_web_push.assert_awaited_once_with(
            "sip_user1", "dev1", {"endpoint": "https://push.example.com/1"},
            "New SMS from +1234567890", "Hello, this is a test SMS.",
            {"type": "sms", "phone_number": "+1234567890", "body": "Hello, this is a test SMS.", "forward_to_gsm": "False"}
        )
        self.assertEqual(result, [{"status": 201, "data": {"message": "Push sent"}}])

    @patch("app.services.webpush.get_web_subscriptions_with_device_id")
    @patch("app.services.webpush.send_web_push", new_callable=AsyncMock)
    async def test_push_web_sms_alert_filter_device(self, mock_send_web_push, mock_get_subscriptions):
        mock_get_subscriptions.return_value = {
            "dev1": {"endpoint": "https://push.example.com/1"},
            "dev2": {"endpoint": "https://push.example.com/2"},
        }
        mock_send_web_push.return_value = {"status": 201, "data": {"message": "Push sent"}}

        result = await push_web_sms_alert("sip_user1", "+1234567890", "Hello", "dev2")

        mock_send_web_push.assert_awaited_once_with(
            "sip_user1", "dev1", {"endpoint": "https://push.example.com/1"},
            "New SMS from +1234567890", "Hello",
            {"type": "sms", "phone_number": "+1234567890", "body": "Hello", "forward_to_gsm": "False"}
        )
        self.assertEqual(result, [{"status": 201, "data": {"message": "Push sent"}}])

    @patch("app.services.webpush.get_vapid_keys")
    @patch("app.services.webpush.webpush")
    async def test_send_web_push_success(self, mock_webpush, mock_get_vapid_keys):
        mock_get_vapid_keys.return_value = VAPID_KEYS
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_webpush.return_value = mock_response

        subscription = {"endpoint": "https://push.example.com/1", "keys": {"p256dh": "p256", "auth": "auth"}}
        data = {"type": "call", "phone_number": "+1234567890"}
        result = await send_web_push("sip_user1", "dev1", subscription, "Incoming Call", "+1234567890", data)

        self.assertEqual(result, {"status": 201, "data": {"message": "Push sent"}})
        kwargs = mock_webpush.call_args.kwargs
        self.assertEqual(kwargs["subscription_info"], subscription)
        self.assertEqual(kwargs["vapid_private_key"], "mock_private_key")
        self.assertEqual(kwargs["vapid_claims"], {"sub": "mailto:admin@example.com"})

    @patch("app.services.webpush.remove_device")
    @patch("app.services.webpush.get_vapid_keys")
    @patch("app.services.webpush.webpush")
    async def test_send_web_push_expired_subscription_removed(self, mock_webpush, mock_get_vapid_keys, mock_remove_device):
        mock_get_vapid_keys.return_value = VAPID_KEYS
        mock_response = MagicMock()
        mock_response.status_code = 410
        mock_webpush.side_effect = WebPushException("Push failed: 410 Gone", response=mock_response)

        subscription = {"endpoint": "https://push.example.com/1", "keys": {"p256dh": "p256", "auth": "auth"}}
        data = {"type": "call", "phone_number": "+1234567890"}
        result = await send_web_push("sip_user1", "dev1", subscription, "Incoming Call", "+1234567890", data)

        self.assertEqual(result["status"], 410)
        mock_remove_device.assert_called_once_with("sip_user1", "dev1")


if __name__ == '__main__':
    unittest.main()
