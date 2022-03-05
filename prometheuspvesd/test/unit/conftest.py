"""Pytest conftest fixtures."""
import os
import sys

import pytest

from prometheuspvesd.utils import Singleton


@pytest.fixture(autouse=True)
def reset_singletons():
    Singleton._instances = {}


@pytest.fixture(autouse=True)
def reset_os_environment():
    os.environ = {}


@pytest.fixture(autouse=True)
def reset_sys_argv():
    sys.argv = ["prometheus-pve-sd"]
