import unittest
from time import sleep
from app import create_app, db
from app.models import User


class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_setter(self):
        u = User(password='123')
        self.assertTrue(u.password_hash is not None)

    def test_no_password_getter(self):
        u = User(password='123')
        with self.assertRaises(AttributeError):
            u.password

    def test_password_verifi123ion(self):
        u = User(password='123')
        self.assertTrue(u.verify_password('123'))
        self.assertFalse(u.verify_password('456'))

    def test_password_salts_are_random(self):
        u = User(password='123')
        u2 = User(password='123')
        self.assertTrue(u.password_hash != u2.password_hash)

    def test_valid_confirmation_token(self):
        u = User(password='123')
        db.session.add(u)
        db.session.commit()
        token = u.generate_confirmation_token()
        self.assertTrue(u.confirm(token))

    def test_invalid_confirmation_token(self):
        u1 = User(password='123')
        u2 = User(password='456')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        token = u1.generate_confirmation_token()
        self.assertFalse(u2.confirm(token))

    def test_expired_confirmation_token(self):
        u = User(password='123')
        db.session.add(u)
        db.session.commit()
        token = u.generate_confirmation_token(1)
        sleep(2)
        self.assertFalse(u.confirm(token))

    def test_valid_reset_token(self):
        u = User(password='123')
        db.session.add(u)
        db.session.commit()
        token = u.generate_reset_token()
        self.assertTrue(u.reset_password(token, '456'))
        self.assertTrue(u.verify_password('456'))

    def test_invalid_reset_token(self):
        u1 = User(password='123')
        u2 = User(password='456')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        token = u1.generate_reset_token()
        self.assertFalse(u2.reset_password(token, '789'))
        self.assertTrue(u2.verify_password('456'))

    def test_roles_and_permissions(self):
        u = User(email='john@example.com', password='123')
        self.assertTrue(u.can(Permission.SUGGEST))
        self.assertFalse(u.can(Permission.APPROVE))

    def test_anonymous_user(self):
        u = AnonymousUser()
        self.assertFalse(u.can(Permission.CHALLENGE))
