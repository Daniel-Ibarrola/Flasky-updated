import pytest
from flasky.app import create_app, db
from flasky.app.models import User, Role


@pytest.fixture
def set_up():
    app = create_app("testing")
    app_context = app.app_context()
    app_context.push()
    db.create_all()

    Role.insert_roles()
    return app, app_context


@pytest.fixture
def tear_down(set_up):
    yield
    _, app_context = set_up
    db.session.remove()
    db.drop_all()
    app_context.pop()


@pytest.mark.usefixtures("tear_down")
def test_gravatar(set_up):
    app, _ = set_up

    u = User(email='john@example.com', password='cat')
    with app.test_request_context('/'):
        gravatar = u.gravatar()
        gravatar_256 = u.gravatar(size=256)
        gravatar_pg = u.gravatar(rating='pg')
        gravatar_retro = u.gravatar(default='retro')

    # assert 'https://secure.gravatar.com/avatar/' + 'd4c74594d841139328695756648b6bd6' in gravatar
    assert 's=256' in gravatar_256
    assert 'r=pg' in gravatar_pg
    assert 'd=retro' in gravatar_retro

