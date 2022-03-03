"""Pytest conftest fixtures."""

import pytest

from prometheuspvesd.utils import Singleton


@pytest.fixture(autouse=True)
def reset_singletons():
    Singleton._instances = {}
