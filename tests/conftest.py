from app import create_app, db
from app.models import Role
import pytest


def set_up():
    app = create_app("testing")
    app_context = app.app_context()
    app_context.push()
    db.create_all()

    Role.insert_roles()
    return app_context


def tear_down(context):
    db.session.remove()
    db.drop_all()
    context.pop()


@pytest.fixture
def set_up_flask_app():
    app_context = set_up()
    yield
    tear_down(app_context)
