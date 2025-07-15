import os
import unittest
import app.database as db

class TestDatabase(unittest.TestCase):

    def setUp(self):
        db.DB_FILE = r'test_data.json'
        if os.path.exists(db.DB_FILE):
            os.remove(db.DB_FILE)
        # Add new device
        db.add_or_update_device({
            "device_id": "dev1",
            "user_name": "user1",
            "user_pass": "pass1",
            "fcm_token": "fcm1",
            "oauth2_token": "token1"
        })

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(db.DB_FILE):
            os.remove(db.DB_FILE)

    def test_load_data(self):
        all_devices = db.load_data()
        self.assertEqual(len(all_devices), 1)
        self.assertEqual(all_devices[0]['user_name'], "user1")

    def test_get_all_devices(self):
        all_devices = db.get_all_devices()
        self.assertEqual(len(all_devices), 1)
        self.assertEqual(all_devices[0]['user_name'], "user1")

    def test_get_device(self):
        device = db.get_device("user1")
        self.assertIsNotNone(device)
        self.assertEqual(device['user_pass'], "pass1")

    def test_update_fcm_token(self):
        resp = db.update_fcm_token("user1", "new_fcm_token")
        self.assertTrue(resp.startswith("FCM token updated"))
        device = db.get_device("user1")
        self.assertEqual(device['fcm_token'], "new_fcm_token")

    def test_update_oauth2_token(self):
        resp = db.update_oauth2_token("user1", "new_oauth_token", 10)
        self.assertTrue(resp.startswith("OAuth2 token updated"))
        device = db.get_device("user1")
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
        resp = db.delete_device("user1")
        self.assertEqual(resp, "Device deleted.")
        self.assertIsNone(db.get_device("user1"))

    def test_delete_device_invalid_user(self):
        resp = db.delete_device("unknown")
        self.assertEqual(resp, "Device not found.")

if __name__ == '__main__':
    unittest.main()