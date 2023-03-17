import time
import unittest
from app.models import User, db


class UserModelTestCase(unittest.TestCase):

    def test_password_setter(self):
        user = User(password="cat")
        self.assertTrue(user.password_hash is not None)

    def test_no_password_getter(self):
        user = User(password="cat")
        with self.assertRaises(AttributeError):
            user.password

    def test_password_verification(self):
        user = User(password="cat")
        self.assertTrue(user.verify_password("cat"))
        self.assertFalse(user.verify_password("dog"))

    def test_password_salts_are_random(self):
        user1 = User(password="cat")
        user2 = User(password="cat")
        self.assertNotEqual(user1.password_hash, user2.password_hash)

    def test_valid_confirmation_token(self):
        user = User(password="cat")
        db.session.add(user)
        db.session.commit()

        token = user.generate_confirmation_token()
        self.assertTrue(user.confirm(token, expiration=3600))

    def test_invalid_generation_token(self):
        user1 = User(password="cat")
        user2 = User(password="cat")
        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()

        token = user1.generate_confirmation_token()
        self.assertFalse(user2.confirm(token))

    def test_expired_confirmation_token(self):
        user = User(password="cat")
        db.session.add(user)
        db.session.commit()

        token = user.generate_confirmation_token()
        time.sleep(2)

        self.assertFalse(user.confirm(token, expiration=1))
