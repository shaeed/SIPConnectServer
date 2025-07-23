import unittest
from unittest.mock import AsyncMock, patch

from app.services.gsm import send_gsm_sms


class TestGsm(unittest.IsolatedAsyncioTestCase):

    @patch('app.services.gsm.get_dongle_id')
    @patch('app.services.gsm.send_sms', new_callable=AsyncMock)
    async def test_send_gsm_sms_success(self, mock_send_sms, mock_get_dongle_id):
        mock_get_dongle_id.return_value = 'dongle0'
        mock_send_sms.return_value = 'Message scheduled to be sent.'

        result = await send_gsm_sms('+1234567890', 'Hello world!', 'alice')
        self.assertEqual(result, 'Message scheduled to be sent.')
        mock_get_dongle_id.assert_called_once_with('alice')
        mock_send_sms.assert_awaited_once_with('+1234567890', 'Hello world!', 'dongle0')

    @patch('app.services.gsm.get_dongle_id')
    @patch('app.services.gsm.send_sms', new_callable=AsyncMock)
    async def test_send_gsm_sms_failure(self, mock_send_sms, mock_get_dongle_id):
        mock_get_dongle_id.return_value = 'dongle0'
        mock_send_sms.return_value = 'Asterisk error. Return code: 1. Log: Some error.'

        result = await send_gsm_sms('+1234567890', 'Hello world!', 'alice')
        self.assertIn('Asterisk error', result)
        mock_get_dongle_id.assert_called_once_with('alice')
        mock_send_sms.assert_awaited_once_with('+1234567890', 'Hello world!', 'dongle0')


if __name__ == '__main__':
    unittest.main()
