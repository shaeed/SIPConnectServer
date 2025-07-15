import unittest
from unittest.mock import patch, MagicMock
import base64

from app.oAuth2_generator import get_authorized_session, decode_jwt_part, get_oauth_token

class TestAuth(unittest.TestCase):
    @patch("app.oAuth2_generator.service_account.Credentials")
    @patch("app.oAuth2_generator.decode_jwt_part")
    def test_get_authorized_session(self, mock_decode_jwt_part, mock_credentials_class):
        mock_credentials = MagicMock()
        mock_credentials.with_always_use_jwt_access.return_value = mock_credentials
        mock_credentials.token = "mock.jwt.token"
        mock_credentials_class.from_service_account_file.return_value = mock_credentials
        mock_decode_jwt_part.return_value = {"exp": 999999999}

        token, expiry = get_authorized_session()
        mock_credentials.refresh.assert_called_once()
        mock_decode_jwt_part.assert_called_once_with("mock.jwt.token")
        self.assertEqual(token, "mock.jwt.token")
        self.assertEqual(expiry, 999999999)

    def test_decode_jwt_part(self):
        header = base64.urlsafe_b64encode(b'{"alg":"HS256"}').rstrip(b'=')
        payload = base64.urlsafe_b64encode(b'{"exp":123456}').rstrip(b'=')
        jwt = header.decode() + "." + payload.decode() + ".signature"

        result = decode_jwt_part(jwt)
        self.assertEqual(result, {"exp": 123456})

    @patch("app.oAuth2_generator.get_oauth2_token")
    @patch("app.oAuth2_generator.update_oauth2_token")
    @patch("app.oAuth2_generator.get_authorized_session")
    @patch("app.oAuth2_generator.time.time")
    def test_get_oauth_token_expired(self, mock_time, mock_get_authorized_session, mock_update, mock_get_token):
        mock_get_token.return_value = {
            "oauth2_token_expiry": 1000,
            "oauth2_token": "expired_token"
        }
        mock_time.return_value = 2000
        mock_get_authorized_session.return_value = ("new_token", 9999)

        token = get_oauth_token("sip_user")
        mock_get_token.assert_called_once_with("sip_user")
        mock_get_authorized_session.assert_called_once()
        mock_update.assert_called_once_with("sip_user", "new_token", 9999)
        self.assertEqual(token, "new_token")

    @patch("app.oAuth2_generator.get_oauth2_token")
    @patch("app.oAuth2_generator.time.time")
    def test_get_oauth_token_valid(self, mock_time, mock_get_token):
        mock_get_token.return_value = {
            "oauth2_token_expiry": 9999,
            "oauth2_token": "valid_token"
        }
        mock_time.return_value = 1000

        token = get_oauth_token("sip_user")
        mock_get_token.assert_called_once_with("sip_user")
        self.assertEqual(token, "valid_token")

    @patch("app.oAuth2_generator.get_oauth2_token")
    def test_get_oauth_token_invalid_user(self, mock_get_token):
        mock_get_token.return_value = None

        with self.assertRaises(Exception) as context:
            get_oauth_token("bad_user")
        self.assertIn("Invalid user", str(context.exception))

if __name__ == '__main__':
    unittest.main()
