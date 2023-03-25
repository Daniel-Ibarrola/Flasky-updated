import time
import pytest
from app.models import User, db


pytestmark = pytest.mark.usefixtures("set_up_flask_app")


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
    user = User(password="cat")
    db.session.add(user)
    db.session.commit()

    token = user.generate_confirmation_token()
    assert user.confirm(token, expiration=3600)


def test_invalid_generation_token():
    user1 = User(password="cat")
    user2 = User(password="cat")
    db.session.add(user1)
    db.session.add(user2)
    db.session.commit()

    token = user1.generate_confirmation_token()
    assert not user2.confirm(token)


def test_expired_confirmation_token():
    user = User(password="cat")
    db.session.add(user)
    db.session.commit()

    token = user.generate_confirmation_token()
    time.sleep(2)

    assert not user.confirm(token, expiration=1)
