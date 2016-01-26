from functools import wraps


def signal_ignore_fixture(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not kwargs.get('raw', False):
            return f(*args, **kwargs)
        else:
            return None
    return wrapper
