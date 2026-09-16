"""Scope archive labels to a service, including its nested article pages."""
from contextvars import ContextVar
from functools import wraps


in_archive = ContextVar('compuserve_archive', default=False)


def archive_service(function):
    @wraps(function)
    def wrapped(*args, **kwargs):
        token = in_archive.set(True)
        try:
            return function(*args, **kwargs)
        finally:
            in_archive.reset(token)
    return wrapped
