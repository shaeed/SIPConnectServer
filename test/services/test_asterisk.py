import unittest
from unittest.mock import AsyncMock, patch

from app.services.asterisk import restart_asterisk, send_sms


class TestAsterisk(unittest.IsolatedAsyncioTestCase):

    @patch('app.services.asterisk.run_in_asterisk', new_callable=AsyncMock)
    async def test_send_sms_success(self, mock_run):
        mock_run.return_value = (0, "OK")
        result = await send_sms("+1234567890", "Hello", "dongle0")
        self.assertEqual(result, "Message scheduled to be sent.")
        mock_run.assert_awaited_once_with('dongle sms dongle0 +1234567890 Hello')

    @patch('app.services.asterisk.run_in_asterisk', new_callable=AsyncMock)
    async def test_send_sms_failure(self, mock_run):
        mock_run.return_value = (1, "Error log")
        result = await send_sms("+1234567890", "Hello", "dongle0")
        self.assertIn("Asterisk error. Return code: 1. Log: Error log", result)
        mock_run.assert_awaited_once_with('dongle sms dongle0 +1234567890 Hello')

    @patch('app.services.asterisk.run_in_asterisk', new_callable=AsyncMock)
    async def test_restart_asterisk_success(self, mock_run):
        mock_run.return_value = (0, "OK")
        result = await restart_asterisk()
        self.assertEqual(result, "Asterisk restarted successfully.")
        mock_run.assert_awaited_once_with('core restart now')

    @patch('app.services.asterisk.run_in_asterisk', new_callable=AsyncMock)
    async def test_restart_asterisk_failure(self, mock_run):
        mock_run.return_value = (1, "Restart failed")
        result = await restart_asterisk()
        self.assertIn("Asterisk failed to restart. Return code: 1. Log: Restart failed", result)
        mock_run.assert_awaited_once_with('core restart now')

    async def test_run_in_asterisk_success(self):
        mock_process = AsyncMock()
        mock_process.communicate.return_value = (b"output", b"")
        mock_process.returncode = 0

        with patch("asyncio.create_subprocess_exec", return_value=mock_process):
            result = await restart_asterisk()
            self.assertEqual(result, "Asterisk restarted successfully.")

    async def test_run_in_asterisk_failure(self):
        mock_process = AsyncMock()
        mock_process.communicate.return_value = (b"", b"error")
        mock_process.returncode = 1

        with patch("asyncio.create_subprocess_exec", return_value=mock_process):
            result = await restart_asterisk()
            self.assertIn("Asterisk failed to restart", result)
            self.assertIn("Return code: 1", result)


if __name__ == '__main__':
    unittest.main()
