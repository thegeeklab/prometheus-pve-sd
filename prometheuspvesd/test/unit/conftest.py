"""Pytest conftest fixtures."""

import logging
import os
import sys
from collections.abc import Generator
from contextlib import contextmanager

import pytest
from _pytest.logging import LogCaptureHandler

from prometheuspvesd.test.unit.test_types import LogContextFactory
from prometheuspvesd.utils import Singleton


@pytest.fixture(autouse=True)
def reset_singletons() -> None:
    Singleton._instances = {}


@pytest.fixture(autouse=True)
def reset_os_environment() -> None:
    os.environ.clear()


@pytest.fixture(autouse=True)
def reset_sys_argv() -> None:
    sys.argv = ["prometheus-pve-sd"]


@contextmanager
def local_caplog_fn(
    level: int = logging.INFO, name: str = "prometheuspvesd"
) -> Generator[LogCaptureHandler]:
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
def local_caplog() -> Generator[LogContextFactory, None, None]:
    """Fixture that yields a context manager for capturing records from non-propagating loggers."""

    yield local_caplog_fn
