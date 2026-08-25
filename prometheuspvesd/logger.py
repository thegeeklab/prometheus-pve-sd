#!/usr/bin/env python3
"""Global utility methods and classes."""

import copy
import logging
import os
import sys
from typing import Any

import colorama
from pythonjsonlogger.json import JsonFormatter

from prometheuspvesd.utils import Singleton, to_bool

JSON_FORMAT = "%(asctime)s %(levelname)s %(message)s"

_LEVEL_COLORS: dict[int, tuple[str, str]] = {
    logging.DEBUG: (colorama.Fore.BLUE, colorama.Style.BRIGHT),
    logging.INFO: (colorama.Fore.CYAN, colorama.Style.BRIGHT),
    logging.WARNING: (colorama.Fore.YELLOW, colorama.Style.BRIGHT),
    logging.ERROR: (colorama.Fore.RED, colorama.Style.BRIGHT),
    logging.CRITICAL: (colorama.Fore.RED, colorama.Style.BRIGHT),
}

_STDOUT_LEVELS = {logging.INFO, logging.WARNING}
_STDERR_LEVELS = {logging.DEBUG, logging.ERROR, logging.CRITICAL}


def _should_do_markup() -> bool:
    py_colors = os.environ.get("PY_COLORS", None)
    if py_colors is not None:
        return to_bool(py_colors)

    return sys.stdout.isatty() and os.environ.get("TERM") != "dumb"


colorama.init(autoreset=True, strip=not _should_do_markup())


class LevelFilter(logging.Filter):
    """Keep only records whose level belongs to the configured level set."""

    def __init__(self, levels: set[int]) -> None:
        super().__init__()
        self._levels = levels

    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno in self._levels


class ConsoleFormatter(logging.Formatter):
    """Colorize the level prefix and reset the color after line breaks."""

    def format(self, record: logging.LogRecord) -> str:
        color, style = _LEVEL_COLORS.get(record.levelno, (colorama.Fore.WHITE, ""))
        reset = colorama.Style.RESET_ALL
        message = record.getMessage().replace("\n", f"\n{reset}... ")
        output = f"{color}{style}[{record.levelname}]{reset} {message}"

        if record.exc_info and not record.exc_text:
            record.exc_text = self.formatException(record.exc_info)
        if record.exc_text:
            if output[-1:] != "\n":
                output += "\n"
            output += record.exc_text

        return output


class MultilineJsonFormatter(JsonFormatter):
    """JSON formatter that replaces line breaks in messages with spaces."""

    def format(self, record: logging.LogRecord) -> str:
        record = copy.copy(record)
        record.msg = record.msg.replace("\n", " ")
        return JsonFormatter.format(self, record)


class Log:
    """Handle logging."""

    def __init__(
        self,
        level: int = logging.WARNING,
        name: str = "prometheuspvesd",
        log_format: str = "console",
    ) -> None:
        self.logger = logging.getLogger(name)
        self.logger.propagate = False
        self.logger.setLevel(level)
        self._configure(log_format)

    def _configure(self, log_format: str) -> None:
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)

        self.logger.addHandler(self._get_handler(sys.stdout, _STDOUT_LEVELS, log_format))
        self.logger.addHandler(self._get_handler(sys.stderr, _STDERR_LEVELS, log_format))

    def _get_handler(self, stream: Any, levels: set[int], log_format: str) -> logging.Handler:
        handler = logging.StreamHandler(stream)
        handler.setLevel(logging.DEBUG)
        handler.addFilter(LevelFilter(levels))
        handler.setFormatter(self._get_formatter(log_format))
        return handler

    def _get_formatter(self, log_format: str) -> logging.Formatter:
        if log_format == "json":
            return MultilineJsonFormatter(JSON_FORMAT)
        if log_format == "simple":
            return logging.Formatter("%(message)s")
        return ConsoleFormatter()

    def update_logger(self, level: int | str, log_format: str) -> None:
        self.logger.setLevel(level)
        self._configure(log_format)

    def sysexit(self, code: int = 1) -> None:
        sys.exit(code)

    def sysexit_with_message(self, msg: str, code: int = 1) -> None:
        self.logger.critical(str(msg))
        self.sysexit(code)


class SingleLog(Log, metaclass=Singleton):
    """Singleton logging class."""

    pass
