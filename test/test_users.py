import unittest
from unittest.mock import patch, AsyncMock, MagicMock

from app import users
from app.models import User


class TestAddUser(unittest.IsolatedAsyncioTestCase):

    async def test_add_user_success(self):
        user = User(
            username="testuser",
            password="abcdef12345",
            audio_interface="ttyA",
            data_interface="ttyB",
            voicemail_number=None
        )

        with patch("app.users.add_or_update_user") as mock_add_or_update_user, \
             patch("app.users.configure_asterisk", new_callable=AsyncMock) as mock_generate_configs, \
             patch("app.users.generate_voicemail_number", return_value=123):
            mock_generate_configs.return_value = "Config done."
            result = await users.add_user(user)

            mock_add_or_update_user.assert_called_once()
            called_args = mock_add_or_update_user.call_args[0][0]
            self.assertEqual(called_args["username"], "testuser")
            self.assertEqual(called_args["voicemail_id"], 123)
            self.assertIn("Config done.", result)

    def test_generate_voicemail_number(self):
        # Simulate that 100 & 101 are taken, so we expect 102
        fake_users = [
            {"voicemail_id": 100},
            {"voicemail_id": 101}
        ]

        with patch("app.users.get_all_users", return_value=fake_users):
            result = users.generate_voicemail_number()
            self.assertEqual(result, 102)


if __name__ == "__main__":
    unittest.main()
