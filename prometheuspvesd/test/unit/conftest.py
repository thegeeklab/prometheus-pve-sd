"""Pytest conftest fixtures."""

import logging
import os
import sys
from contextlib import contextmanager

import pytest
from _pytest.logging import LogCaptureHandler

from prometheuspvesd.utils import Singleton


@pytest.fixture(autouse=True)
def reset_singletons():
    Singleton._instances = {}


@pytest.fixture(autouse=True)
def reset_os_environment():
    os.environ.clear()


@pytest.fixture(autouse=True)
def reset_sys_argv():
    sys.argv = ["prometheus-pve-sd"]


@contextmanager
def local_caplog_fn(level=logging.INFO, name="prometheuspvesd"):
    """
    Context manager that captures records from non-propagating loggers.

    After the end of the 'with' statement, the log level is restored to its original
    value. Code adapted from https://github.com/pytest-dev/pytest/issues/3697#issuecomment-790925527.

    :param int level: The level.
    :param logging.Logger logger: The logger to update.
    """

    logger = logging.getLogger(name)

    old_level = logger.level
    logger.setLevel(level)

    handler = LogCaptureHandler()
    logger.addHandler(handler)

    try:
        yield handler
    finally:
        logger.setLevel(old_level)
        logger.removeHandler(handler)


@pytest.fixture
def local_caplog():
    """Fixture that yields a context manager for capturing records from non-propagating loggers."""

    yield local_caplog_fn
