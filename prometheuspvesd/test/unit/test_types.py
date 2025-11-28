"""Shared type aliases for tests."""

from collections.abc import Callable
from contextlib import _GeneratorContextManager
from typing import TypeAlias

from _pytest.logging import LogCaptureHandler

# The type of the actual context manager instance
LogContextManager: TypeAlias = _GeneratorContextManager[LogCaptureHandler, None, None]

# The type of the factory function (the fixture yields this)
# It takes (int, str) arguments and returns the LogContextManager
LogContextFactory: TypeAlias = Callable[..., LogContextManager]
