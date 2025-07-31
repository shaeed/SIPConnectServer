import unittest
from unittest.mock import patch, AsyncMock, MagicMock, Mock

import app.asterisk_config_generator as config_generator

class TestConfigGenerator(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        # dummy user data
        self.user_data = {
            'username': 'shaeed',
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

        mock_file = MagicMock()
        mock_file.read = AsyncMock(return_value=fake_file_content)
        mock_file.write = AsyncMock()
        # Make mock file as Async context manager
        mock_file.__aenter__ = AsyncMock(return_value=mock_file)

        mock_path = Mock()
        mock_path.exists.return_value = True
        with patch("aiofiles.open", return_value=mock_file), \
                patch("app.asterisk_config_generator.Path", return_value=mock_path):
            await config_generator.update_file(
                header="header line",
                content=["line1", "line2"],
                path="dummy.conf",
                replace=False
            )
        mock_file.read.assert_awaited_once()
        mock_file.write.assert_awaited_once()
        written_content = mock_file.write.call_args[0][0]
        self.assertIn("old content", written_content)
        self.assertNotIn("some content", written_content)
        self.assertIn(config_generator.edit_section_identifier, written_content)
        self.assertIn("header line", written_content)
        self.assertIn("line1", written_content)
        self.assertIn("line2", written_content)

    async def test_update_file_replace_false_old_file_not_exists(self):
        fake_file_content = f"old content\n{config_generator.edit_section_identifier}\nsome content"

        mock_file = MagicMock()
        mock_file.read = AsyncMock(return_value=fake_file_content)
        mock_file.write = AsyncMock()
        # make mock_file as Async context manager
        mock_file.__aenter__ = AsyncMock(return_value=mock_file)

        mock_path = Mock()
        mock_path.exists.return_value = False
        with patch("aiofiles.open", return_value=mock_file), \
                patch("app.asterisk_config_generator.Path", return_value=mock_path):
            await config_generator.update_file(
                header="header line",
                content=["line1", "line2"],
                path="dummy.conf",
                replace=False
            )
        mock_file.read.assert_not_awaited()
        mock_file.write.assert_awaited_once()
        written_content = mock_file.write.call_args[0][0]
        self.assertNotIn("old content", written_content)
        self.assertNotIn("some content", written_content)
        self.assertIn(config_generator.edit_section_identifier, written_content)
        self.assertIn("header line", written_content)
        self.assertIn("line1", written_content)
        self.assertIn("line2", written_content)

    async def test_generate_configs(self):
        fake_users = [{
            "username": "bob",
            "user_pass": "pw",
            "dongle_audio_interface": "ttyA",
            "dongle_data_interface": "ttyB",
            "voicemail_id": "1001"
        }]

        with patch("app.asterisk_config_generator.get_all_users", return_value=fake_users), \
                patch("app.asterisk_config_generator.dongle_template", "{dongle_id}"), \
                patch("app.asterisk_config_generator.pjsip_template", "{pjsip_user}"), \
                patch("app.asterisk_config_generator.extension_template", "{ext_sip_user}"), \
                patch("app.asterisk_config_generator.update_file") as mock_update_file:
            result = await config_generator.generate_configs()
            self.assertEqual(result, "Asterisk config generated successfully.")
            mock_update_file.assert_awaited()
            self.assertEqual(mock_update_file.await_count, 3)

if __name__ == '__main__':
    unittest.main()
