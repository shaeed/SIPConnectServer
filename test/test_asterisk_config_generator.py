import unittest
from unittest.mock import patch, mock_open

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

    @patch('builtins.open', new_callable=mock_open, read_data='existing content\n;******** Auto generated lines below ********\nold config')
    def test_update_file_appends_content(self, mock_file):
        config_generator.update_file(
            header='header line',
            content=['line1', 'line2'],
            path='/fake/path.conf',
            replace=False
        )

        # Check that open was called for read and write
        mock_file.assert_any_call('/fake/path.conf', 'r')
        mock_file.assert_any_call('/fake/path.conf', 'w')

        # The final written content should not contain 'old config'
        handle = mock_file()
        written_content = handle.write.call_args[0][0]

        self.assertIn('existing content', written_content)
        self.assertIn('header', written_content)
        self.assertIn('line1', written_content)
        self.assertIn('line2', written_content)
        self.assertNotIn('old config', written_content)

    @patch('builtins.open', new_callable=mock_open)
    def test_update_file_replace_true(self, mock_file):
        # If replace=True it should not read the file, only write
        config_generator.update_file(
            header='header line',
            content=['line1', 'line2'],
            path='/fake/path.conf',
            replace=True
        )
        # Should only open for write
        mock_file.assert_called_with('/fake/path.conf', 'w')
        handle = mock_file()
        written_content = handle.write.call_args[0][0]
        self.assertNotIn('existing content', written_content)
        self.assertIn('header line', written_content)
        self.assertIn('line1', written_content)
        self.assertIn('line2', written_content)

    @patch('app.asterisk_config_generator.get_all_users')
    @patch('app.asterisk_config_generator.update_file')
    def test_generate(self, mock_update_file, mock_get_all_users):
        # Mock template values to avoid import errors
        config_generator.dongle_template = "dongle {dongle_id}"
        config_generator.pjsip_template = "pjsip {pjsip_user}"
        config_generator.extension_template = "ext {ext_gsm_incoming}"
        config_generator.dongle_header = "[dongle]"
        config_generator.pjsip_header = "[pjsip]"
        config_generator.extension_header = "[extension]"
        # Mock user list
        mock_get_all_users.return_value = [self.user_data]

        config_generator.generate()
        # It should call update_file three times
        self.assertEqual(mock_update_file.call_count, 3)
        # Check one call's arguments
        args, kwargs = mock_update_file.call_args
        self.assertIn(args[0], ['[dongle]', '[pjsip]', '[extension]'])

if __name__ == '__main__':
    unittest.main()
