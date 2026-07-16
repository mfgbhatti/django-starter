"""
Django project environment file
"""

import environ
from django.core.exceptions import ImproperlyConfigured

env = environ.Env()

# base directory path will be from setting file
# BASE_DIR = Path(__file__).resolve().parent.parent

# this is for tree -L 2 i.e. file -> folder -> root
BASE_DIR = environ.Path(__file__) - 2


def env_to_enum(enum_cls, value):
    for x in enum_cls:
        if x.value == value:
            return x

    raise ImproperlyConfigured(
        f"Env value {repr(value)} could not be found in {repr(enum_cls)}"
    )
