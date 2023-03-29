from datetime import datetime
import time
import pytest
from app import db
from app.models import AnonymousUser, User, Permission, Role


pytestmark = pytest.mark.usefixtures("set_up_flask_app")


def add_user_to_db(password, email=None):
    user = User(password="cat", email=email)
    db.session.add(user)
    db.session.commit()
    return user


def test_password_setter():
    user = User(password="cat")
    assert user.password_hash is not None


def test_no_password_getter():
    user = User(password="cat")
    with pytest.raises(AttributeError):
        user.password


def test_password_verification():
    user = User(password="cat")
    assert user.verify_password("cat")
    assert not user.verify_password("dog")


def test_password_salts_are_random():
    user1 = User(password="cat")
    user2 = User(password="cat")
    assert user1.password_hash != user2.password_hash


def test_valid_confirmation_token():
    user = add_user_to_db(password="cat")
    token = user.generate_confirmation_token()
    assert user.confirm(token, expiration=3600)


def test_invalid_generation_token():
    user1 = add_user_to_db(password="cat")
    user2 = add_user_to_db(password="cat")
    token = user1.generate_confirmation_token()
    assert not user2.confirm(token)


def test_expired_confirmation_token():
    user = add_user_to_db(password="cat")
    token = user.generate_confirmation_token()
    time.sleep(2)
    assert not user.confirm(token, expiration=1)


def test_valid_reset_token():
    user = add_user_to_db(password="cat")
    token = user.generate_reset_token()
    assert User.reset_password(token, "dog")
    assert user.verify_password("dog")


def test_invalid_reset_token():
    user = add_user_to_db(password="cat")
    token = user.generate_reset_token()
    assert not User.reset_password(token + "a", "horse")
    assert user.verify_password("cat")


def test_valid_email_change_token():
    user = add_user_to_db(email="john@example.com", password="cat")
    token = user.generate_email_change_token("susan@example.org")
    assert user.change_email(token)
    assert user.email == "susan@example.org"


def test_invalid_email_change_token():
    user1 = add_user_to_db(email="john@example.com", password="cat")
    user2 = add_user_to_db(email="susan@example.org", password="dog")
    token = user1.generate_email_change_token("david@example.com")
    assert not user2.change_email(token)
    assert user2.email == "susan@example.org"
    assert user1.email == "john@example.com"


def test_duplicate_email_change_token():
    user1 = add_user_to_db(email="john@example.com", password="cat")
    user2 = add_user_to_db(email="susan@example.org", password="dog")
    token = user2.generate_email_change_token("john@example.com")
    assert not user2.change_email(token)
    assert user2.email == "susan@example.org"


def test_user_role():
    user = User(email="john@example.com", password="cat")
    assert user.can(Permission.FOLLOW)
    assert user.can(Permission.COMMENT)
    assert user.can(Permission.WRITE)
    assert not user.can(Permission.MODERATE)
    assert not user.can(Permission.ADMIN)


def test_anonymous_user():
    user = AnonymousUser()
    assert not user.can(Permission.FOLLOW)
    assert not user.can(Permission.COMMENT)
    assert not user.can(Permission.WRITE)
    assert not user.can(Permission.MODERATE)
    assert not user.can(Permission.ADMIN)


def test_moderator_role():
    role = Role.query.filter_by(name="Moderator").first()
    user = User(email="john@example.com", password="cat", role=role)
    assert user.can(Permission.FOLLOW)
    assert user.can(Permission.COMMENT)
    assert user.can(Permission.WRITE)
    assert user.can(Permission.MODERATE)
    assert not user.can(Permission.ADMIN)


def test_admin_role():
    role = Role.query.filter_by(name="Administrator").first()
    user = User(email="john@example.com", password="cat", role=role)
    assert user.is_administrator()


def test_timestamps():
    user = add_user_to_db(password="cat")
    assert (datetime.utcnow() - user.member_since).total_seconds() < 3
    assert (datetime.utcnow() - user.last_seen).total_seconds() < 3


def test_ping():
    user = add_user_to_db(password="cat")
    time.sleep(2)
    last_seen_before = user.last_seen
    user.ping()
    assert user.last_seen > last_seen_before
