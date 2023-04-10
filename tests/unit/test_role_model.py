import pytest

from app.models import db, Role, Permission

pytestmark = pytest.mark.usefixtures("set_up_flask_app")


def test_add_permissions_to_role():
    role = Role(name="role")
    role.add_permission(Permission.COMMENT)
    role.add_permission(Permission.WRITE_ARTICLES)

    assert role.has_permission(Permission.COMMENT)
    assert role.has_permission(Permission.WRITE_ARTICLES)


def test_remove_permissions_from_role():
    role = Role(name="role")
    role.add_permission(Permission.COMMENT)
    role.add_permission(Permission.WRITE_ARTICLES)

    role.remove_permission(Permission.WRITE_ARTICLES)

    assert role.has_permission(Permission.COMMENT)
    assert not role.has_permission(Permission.WRITE_ARTICLES)


def test_reset_permissions():
    role = Role(name="role")
    role.add_permission(Permission.COMMENT)
    role.add_permission(Permission.WRITE_ARTICLES)

    role.reset_permissions()

    assert not role.has_permission(Permission.COMMENT)
    assert not role.has_permission(Permission.WRITE_ARTICLES)
