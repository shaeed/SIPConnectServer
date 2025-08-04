import os
import unittest
import app.database as db

class TestDatabase(unittest.TestCase):

    def setUp(self):
        db.DB_FILE = r'test_data.json'
        db._DB_FULL = {
            "app-config": {
                "service_account_file": "uploads/test-file.json",
                "firebase_project_id": "test-project"
            },
            "users": [{
                "username": "user1",
                "user_pass": "pass1",
                "devices": {
                    "dev1": {
                        "device_id": "dev1",
                        "fcm_token": "test_fcm_token"
                    }
                },
                "oauth2_token": "token1"
            }]
        }
        db._DB_DATA = db._DB_FULL["users"]

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(db.DB_FILE):
            os.remove(db.DB_FILE)

    def test_load_data(self):
        all_devices = db.load_data()
        self.assertEqual(len(all_devices), 1)
        self.assertEqual(all_devices[0]['username'], "user1")

    def test_get_all_devices(self):
        all_devices = db.get_all_users()
        self.assertEqual(len(all_devices), 1)
        self.assertEqual(all_devices[0]['username'], "user1")

    def test_get_device(self):
        device = db.get_user_data("user1")
        self.assertIsNotNone(device)
        self.assertEqual(device['user_pass'], "pass1")

    def test_update_fcm_token(self):
        resp = db.update_fcm_token("user1", "dev1", "new_fcm_token")
        self.assertTrue(resp.startswith("FCM token updated"))
        new_tokens = db.get_fcm_tokens("user1")
        self.assertEqual(new_tokens, ["new_fcm_token"])

    def test_get_fcm_tokens(self):
        tokens = db.get_fcm_tokens('user1')
        self.assertEqual(tokens, ['test_fcm_token'])

    def test_get_fcm_tokens_no_device(self):
        del db._DB_DATA[0]['devices']
        tokens = db.get_fcm_tokens('user1')
        self.assertEqual(tokens, [])

    def test_get_fcm_token(self):
        # device exists
        token = db.get_fcm_token('user1', 'dev1')
        self.assertEqual(token, 'test_fcm_token')
        # device not exists
        tokens = db.get_fcm_token('user1', 'dev2')
        self.assertIsNone(tokens)
        # user not exists
        tokens = db.get_fcm_token('user2', 'dev2')
        self.assertIsNone(tokens)

    def test_get_fcm_tokens_with_device_id(self):
        tokens = db.get_fcm_tokens_with_device_id('user1')
        self.assertDictEqual(tokens, {'dev1': 'test_fcm_token'})

    def test_update_fcm_token_2_devices(self):
        resp = db.update_fcm_token("user1", "dev1", "new_fcm_token")
        resp = db.update_fcm_token("user1", "dev2", "new_fcm_token2")
        self.assertTrue(resp.startswith("FCM token updated"))
        new_tokens = db.get_fcm_tokens("user1")
        self.assertEqual(new_tokens, ["new_fcm_token", "new_fcm_token2"])

    def test_update_oauth2_token(self):
        resp = db.update_oauth2_token("user1", "new_oauth_token", 10)
        self.assertTrue(resp.startswith("OAuth2 token updated"))
        device = db.get_user_data("user1")
        self.assertEqual(device['oauth2_token'], "new_oauth_token")
        self.assertIsInstance(device['oauth2_token_expiry'], int)

    def test_get_oauth2_token(self):
        oauth_info = db.get_oauth2_token("user1")
        self.assertEqual(oauth_info['oauth2_token'], "token1")
        self.assertIsInstance(oauth_info['oauth2_token_expiry'], int)

    def test_get_oauth2_token_not_found(self):
        oauth_info = db.get_oauth2_token("user2")
        self.assertDictEqual(oauth_info, {})

    def test_user_exits(self):
        resp = db.user_exits('user1')
        self.assertIsNotNone(resp)

    def test_user_exits_false(self):
        resp = db.user_exits('user1')
        self.assertTrue(resp)

    def test_delete_device(self):
        resp = db.delete_user("user1")
        self.assertEqual(resp, "User user1 deleted.")
        self.assertIsNone(db.get_user_data("user1"))

    def test_delete_device_invalid_user(self):
        resp = db.delete_user("unknown")
        self.assertEqual(resp, "User unknown not found.")

    def test_get_project_id(self):
        project_id = db.get_project_id()
        self.assertEqual(project_id, 'test-project')

    def test_set_project_id(self):
        db.set_project_id('new-test-project')
        project_id = db.get_project_id()
        self.assertEqual(project_id, 'new-test-project')

    def test_get_service_account_file_path(self):
        file_path = db.get_service_account_file_path()
        self.assertEqual(file_path, 'uploads/test-file.json')

    def test_set_service_account_file_path(self):
        db.set_service_account_file_path('new_file_path.json')
        file_path = db.get_service_account_file_path()
        self.assertEqual(file_path, 'new_file_path.json')

if __name__ == '__main__':
    unittest.main()