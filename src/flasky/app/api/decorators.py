from functools import wraps
from flask import g
from flasky.app.api.errors import forbidden


def permission_required(permission):
    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            if not g.current_user.can(permission):
                return forbidden("Insuficcient permissions")
            return func(*args, *kwargs)
        return decorated_function
    return decorator
