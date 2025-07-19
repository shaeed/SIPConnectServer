import unittest
from unittest.mock import patch, AsyncMock

import app.asterisk_config_generator as config_generator

class TestConfigGenerator(unittest.TestCase):

    def setUp(self):
        # dummy user data
        self.user_data = {
            'user_name': 'shaeed',
            'user_pass': 'secret',
            'dongle_audio_interface': 'audio0',
            'dongle_data_interface': 'data0',
            'voicemail_id': '1001'
        }

    def test_get_config_variables(self):
        expected = {
            'dongle_id': 'dongle_shaeed',
            'dongle_audio': 'audio0',
            'dongle_data': 'data0',
            'dongle_context': 'gsmin_dongle_shaeed',
            'dongle_smscontext': 'gsmin_dongle_shaeed',
            'pjsip_auth': 'shaeed_auth',
            'pjsip_user': 'shaeed',
            'pjsip_pass': 'secret',
            'pjsip_context': 'voipin_shaeed',
            'pjsip_callerid': '1001',
            'ext_sip_user': 'shaeed',
            'ext_dongle_id': 'dongle_shaeed',
            'ext_gsm_incoming': 'gsmin_dongle_shaeed',
            'ext_voip_incoming': 'voipin_shaeed',
            'ext_gsm_outgoing': 'gsmout_dongle_shaeed',
            'ext_gsm_outgoing_sms': 'smsout_dongle_shaeed',
        }
        variables = config_generator.get_config_variables(self.user_data)
        self.assertEqual(expected, variables)

    async def test_update_file_replace_true(self):
        mock_file = AsyncMock()
        mock_open_file = AsyncMock()
        mock_open_file.__aenter__.return_value = mock_file

        with patch("aiofiles.open", return_value=mock_open_file):
            await config_generator.update_file(
                header="header line",
                content=["line1", "line2"],
                path="dummy.conf",
                replace=True
            )
        mock_file.write.assert_called_once()
        written_content = mock_file.write.call_args[0][0]
        self.assertIn(config_generator.edit_section_identifier, written_content)
        self.assertIn("header line", written_content)
        self.assertIn("line1", written_content)
        self.assertIn("line2", written_content)

    async def test_update_file_replace_false_reads_old_file(self):
        fake_file_content = f"old content\n{config_generator.edit_section_identifier}\nsome content"
        mock_read_file = AsyncMock()
        mock_read_file.read.return_value = fake_file_content
        mock_write_file = AsyncMock()
        mock_open = AsyncMock(side_effect=[AsyncMock(__aenter__=AsyncMock(return_value=mock_read_file)),
                                           AsyncMock(__aenter__=AsyncMock(return_value=mock_write_file))])

        with patch("aiofiles.open", mock_open):
            await config_generator.update_file(
                header="header line",
                content=["line1", "line2"],
                path="dummy.conf",
                replace=False
            )
        mock_read_file.read.assert_awaited_once()
        mock_write_file.write.assert_awaited_once()
        written_content = mock_write_file.write.call_args[0][0]
        self.assertIn("old content", written_content)
        self.assertNotIn("some content", written_content)
        self.assertIn(config_generator.edit_section_identifier, written_content)
        self.assertIn("header line", written_content)
        self.assertIn("line1", written_content)
        self.assertIn("line2", written_content)

    async def test_generate_configs(self):
        fake_users = [{
            "user_name": "bob",
            "user_pass": "pw",
            "dongle_audio_interface": "ttyA",
            "dongle_data_interface": "ttyB",
            "voicemail_id": "1001"
        }]

        with patch("app.config_generator.get_all_users", return_value=fake_users), \
                patch("app.config_generator.dongle_template", "{dongle_id}"), \
                patch("app.config_generator.pjsip_template", "{pjsip_user}"), \
                patch("app.config_generator.extension_template", "{ext_sip_user}"), \
                patch("aiofiles.open", new_callable=AsyncMock) as mock_open:
            mock_write_file = AsyncMock()
            mock_open.return_value.__aenter__.return_value = mock_write_file

            result = await config_generator.generate_configs()
            self.assertEqual(result, "Asterisk config generated successfully.")
            self.assertEqual(mock_write_file.write.await_count, 3)

    async def test_restart_asterisk_success(self):
        mock_process = AsyncMock()
        mock_process.communicate.return_value = (b"output", b"")
        mock_process.returncode = 0

        with patch("asyncio.create_subprocess_exec", return_value=mock_process):
            result = await config_generator.restart_asterisk()
            self.assertEqual(result, "Asterisk restarted successfully.")

    async def test_restart_asterisk_failure(self):
        mock_process = AsyncMock()
        mock_process.communicate.return_value = (b"", b"error")
        mock_process.returncode = 1

        with patch("asyncio.create_subprocess_exec", return_value=mock_process):
            result = await config_generator.restart_asterisk()
            self.assertIn("Asterisk failed to restart", result)
            self.assertIn("Return code: 1", result)

if __name__ == '__main__':
    unittest.main()
