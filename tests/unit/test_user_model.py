import time
import pytest
from app.models import User, db


pytestmark = pytest.mark.usefixtures("set_up_flask_app")


def add_user_to_db(password):
    user = User(password="cat")
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
