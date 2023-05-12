from flasky.app import create_app, db
from flasky.app.models import Role
import pytest


def set_up():
    app = create_app("testing")
    app_context = app.app_context()
    app_context.push()
    db.create_all()

    Role.insert_roles()
    return app, app_context


def tear_down(context):
    db.session.remove()
    db.drop_all()
    context.pop()


@pytest.fixture
def set_up_flask_app():
    app, app_context = set_up()
    yield
    tear_down(app_context)


@pytest.fixture()
def client():
    app, app_context = set_up()
    client = app.test_client(use_cookies=True)
    yield client
    tear_down(app_context)


@pytest.fixture()
def client_no_cookies():
    app, app_context = set_up()
    client = app.test_client(use_cookies=False)
    yield client
    tear_down(app_context)
