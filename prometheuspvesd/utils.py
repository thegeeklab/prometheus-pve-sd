#!/usr/bin/env python3
"""Global utility methods and classes."""

from distutils.util import strtobool
from typing import ClassVar


def to_bool(string):
    return bool(strtobool(str(string)))


class Singleton(type):
    """Meta singleton class."""

    _instances: ClassVar[dict] = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]
