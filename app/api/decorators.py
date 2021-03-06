from functools import wraps
from flask import g
from .errors import forbidden


def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwars):
            if not g.current_user.can(permission):
                return forbidden('Insufficent permissions')
            return f(*args, **kwargs)

        return decorated_function

    return decorator
