import unittest
from unittest.mock import AsyncMock, patch

import app.services.asterisk as asterisk


class TestAsterisk(unittest.IsolatedAsyncioTestCase):

    @patch('app.services.asterisk.run_in_asterisk', new_callable=AsyncMock)
    async def test_send_sms_success(self, mock_run):
        mock_run.return_value = (0, "OK")
        result = await asterisk.send_sms("+1234567890", "Hello", "dongle0")
        self.assertEqual(result, "Message scheduled to be sent.")
        mock_run.assert_awaited_once_with('dongle sms dongle0 +1234567890 Hello')

    @patch('app.services.asterisk.run_in_asterisk', new_callable=AsyncMock)
    async def test_send_sms_failure(self, mock_run):
        mock_run.return_value = (1, "Error log")
        result = await asterisk.send_sms("+1234567890", "Hello", "dongle0")
        self.assertIn("Asterisk error. Return code: 1. Log: Error log", result)
        mock_run.assert_awaited_once_with('dongle sms dongle0 +1234567890 Hello')

    @patch('app.services.asterisk.run_in_asterisk', new_callable=AsyncMock)
    async def test_restart_asterisk_success(self, mock_run):
        mock_run.return_value = (0, "OK")
        result = await asterisk.restart_asterisk()
        self.assertEqual(result, "Asterisk restarted successfully.")
        mock_run.assert_awaited_once_with('core restart now')

    @patch('app.services.asterisk.run_in_asterisk', new_callable=AsyncMock)
    async def test_restart_asterisk_failure(self, mock_run):
        mock_run.return_value = (1, "Restart failed")
        result = await asterisk.restart_asterisk()
        self.assertIn("Asterisk failed to restart. Return code: 1. Log: Restart failed", result)
        mock_run.assert_awaited_once_with('core restart now')

    async def test_run_in_asterisk_success(self):
        mock_process = AsyncMock()
        mock_process.communicate.return_value = (b"output", b"")
        mock_process.returncode = 0

        with patch("asyncio.create_subprocess_exec", return_value=mock_process):
            result = await asterisk.restart_asterisk()
            self.assertEqual(result, "Asterisk restarted successfully.")

    async def test_run_in_asterisk_failure(self):
        mock_process = AsyncMock()
        mock_process.communicate.return_value = (b"", b"error")
        mock_process.returncode = 1

        with patch("asyncio.create_subprocess_exec", return_value=mock_process):
            result = await asterisk.restart_asterisk()
            self.assertIn("Asterisk failed to restart", result)
            self.assertIn("Return code: 1", result)

    @patch("app.services.asterisk.aiofiles.open")
    @patch("app.services.asterisk.update_file", new_callable=AsyncMock)
    async def test_update_rtp_ports(self, mock_update_file, mock_open):
        mock_file = AsyncMock()
        mock_file.read = AsyncMock(return_value="\nrtpstart=5000\nrtpend=6000\n")
        mock_open.return_value.__aenter__.return_value = mock_file
        await asterisk.update_rtp_ports(10000, 10060)

        mock_open.assert_called_once_with(asterisk.RTP_FILE, 'r')
        args, kwargs = mock_update_file.call_args
        self.assertEqual(args[0], '')  # first arg
        self.assertIn("rtpstart=10000", args[1][0])
        self.assertIn("rtpend=10060", args[1][0])
        self.assertEqual(args[2], asterisk.RTP_FILE)
        self.assertTrue(args[3])

    @patch("app.services.asterisk.aiofiles.open")
    @patch("app.services.asterisk.update_file", new_callable=AsyncMock)
    async def test_update_rtp_ports_2(self, mock_update_file, mock_open):
        fake_file = """
;
; RTP Configuration
;
[general]
;
; RTP start and RTP end configure start and end addresses
;
; Defaults are rtpstart=5000 and rtpend=31000
;
rtpstart=10000
rtpend=10100
;
; Whether to enable or disable UDP checksums on RTP traffic
;
;rtpchecksums=no
;
; The amount of time a DTMF digit with no 'end' marker should be
; allowed to continue (in 'samples', 1/8000 of a second)
;
;dtmftimeout=3000
; rtcpinterval = 5000   ; Milliseconds between rtcp reports
                        ;(min 500, max 60000, default 5000)
        """
        mock_file = AsyncMock()
        mock_file.read = AsyncMock(return_value=fake_file)
        mock_open.return_value.__aenter__.return_value = mock_file
        await asterisk.update_rtp_ports(10000, 10800)

        expected = """
;
; RTP Configuration
;
[general]
;
; RTP start and RTP end configure start and end addresses
;
; Defaults are rtpstart=5000 and rtpend=31000
;
rtpstart=10000
rtpend=10800
;
; Whether to enable or disable UDP checksums on RTP traffic
;
;rtpchecksums=no
;
; The amount of time a DTMF digit with no 'end' marker should be
; allowed to continue (in 'samples', 1/8000 of a second)
;
;dtmftimeout=3000
; rtcpinterval = 5000   ; Milliseconds between rtcp reports
                        ;(min 500, max 60000, default 5000)
        """
        mock_open.assert_called_once_with(asterisk.RTP_FILE, 'r')
        args, kwargs = mock_update_file.call_args
        self.assertEqual(args[0], '')  # first arg
        self.assertEqual(expected, args[1][0])
        self.assertEqual(args[2], asterisk.RTP_FILE)
        self.assertTrue(args[3])

    @patch("app.services.asterisk.update_rtp_ports", new_callable=AsyncMock)
    async def test_first_time_init(self, mock_update_rtp_ports):
        await asterisk.first_time_init()
        mock_update_rtp_ports.assert_awaited_once_with(10000, 10060)

    async def test_configure_asterisk(self):
        with patch("app.services.asterisk.first_time_init"), \
             patch("app.services.asterisk.generate_configs", return_value="Config generated") as mock_generate_configs, \
             patch("app.services.asterisk.restart_asterisk", return_value="Asterisk restarted") :
            result = await asterisk.configure_asterisk()
            self.assertIn("Config generated", result)
            self.assertIn("Asterisk restarted", result)

    async def test_configure_asterisk_exception(self):
        with patch("app.services.asterisk.first_time_init"), \
             patch("app.services.asterisk.generate_configs", new_callable=AsyncMock) as mock_generate_configs, \
             patch("app.services.asterisk.restart_asterisk", return_value=123) :
            mock_generate_configs.side_effect = Exception("Oops!")

            result = await asterisk.configure_asterisk()
            self.assertIn("Either config generation or Asterisk restart failed", result)
            self.assertIn("Oops!", result)


if __name__ == '__main__':
    unittest.main()
