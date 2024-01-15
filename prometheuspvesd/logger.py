#!/usr/bin/env python3
"""Global utility methods and classes."""

import logging
import os
import sys

import colorama
from pythonjsonlogger import jsonlogger

from prometheuspvesd.utils import Singleton, to_bool

CONSOLE_FORMAT = "{}{}[%(levelname)s]{} %(message)s"
JSON_FORMAT = "%(asctime)s %(levelname)s %(message)s"


def _should_do_markup():
    py_colors = os.environ.get("PY_COLORS", None)
    if py_colors is not None:
        return to_bool(py_colors)

    return sys.stdout.isatty() and os.environ.get("TERM") != "dumb"


colorama.init(autoreset=True, strip=not _should_do_markup())


class LogFilter:
    """A custom log filter which excludes log messages above the logged level."""

    def __init__(self, level):
        """
        Initialize a new custom log filter.

        :param level: Log level limit
        :returns: None

        """
        self.__level = level

    def filter(self, logRecord):  # noqa
        # https://docs.python.org/3/library/logging.html#logrecord-attributes
        return logRecord.levelno <= self.__level


class SimpleFormatter(logging.Formatter):
    """Logging Formatter for simple logs."""

    def format(self, record):
        return logging.Formatter.format(self, record)


class MultilineFormatter(logging.Formatter):
    """Logging Formatter to reset color after newline characters."""

    def format(self, record):
        record.msg = record.msg.replace("\n", f"\n{colorama.Style.RESET_ALL}... ")
        return logging.Formatter.format(self, record)


class MultilineJsonFormatter(jsonlogger.JsonFormatter):
    """Logging Formatter to remove newline characters."""

    def format(self, record):
        record.msg = record.msg.replace("\n", " ")
        return jsonlogger.JsonFormatter.format(self, record)


class Log:
    """Handle logging."""

    def __init__(self, level=logging.WARNING, name="prometheuspvesd", log_format="console"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.logger.addHandler(self._get_error_handler(log_format))
        self.logger.addHandler(self._get_warning_handler(log_format))
        self.logger.addHandler(self._get_info_handler(log_format))
        self.logger.addHandler(self._get_critical_handler(log_format))
        self.logger.addHandler(self._get_debug_handler(log_format))
        self.logger.propagate = False

    def _get_error_handler(self, log_format):
        handler = logging.StreamHandler(sys.stderr)
        handler.setLevel(logging.ERROR)
        handler.addFilter(LogFilter(logging.ERROR))

        if log_format == "json":
            handler.setFormatter(MultilineJsonFormatter(JSON_FORMAT))
        elif log_format == "simple":
            handler.setFormatter(SimpleFormatter())
        else:
            handler.setFormatter(
                MultilineFormatter(
                    self.error(
                        CONSOLE_FORMAT.format(
                            colorama.Fore.RED, colorama.Style.BRIGHT, colorama.Style.RESET_ALL
                        )
                    )
                )
            )

        return handler

    def _get_warning_handler(self, log_format):
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.WARNING)
        handler.addFilter(LogFilter(logging.WARNING))

        if log_format == "json":
            handler.setFormatter(MultilineJsonFormatter(JSON_FORMAT))
        elif log_format == "simple":
            handler.setFormatter(SimpleFormatter())
        else:
            handler.setFormatter(
                MultilineFormatter(
                    self.warning(
                        CONSOLE_FORMAT.format(
                            colorama.Fore.YELLOW, colorama.Style.BRIGHT, colorama.Style.RESET_ALL
                        )
                    )
                )
            )

        return handler

    def _get_info_handler(self, log_format):
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)
        handler.addFilter(LogFilter(logging.INFO))

        if log_format == "json":
            handler.setFormatter(MultilineJsonFormatter(JSON_FORMAT))
        elif log_format == "simple":
            handler.setFormatter(SimpleFormatter())
        else:
            handler.setFormatter(
                MultilineFormatter(
                    self.info(
                        CONSOLE_FORMAT.format(
                            colorama.Fore.CYAN, colorama.Style.BRIGHT, colorama.Style.RESET_ALL
                        )
                    )
                )
            )

        return handler

    def _get_critical_handler(self, log_format):
        handler = logging.StreamHandler(sys.stderr)
        handler.setLevel(logging.CRITICAL)
        handler.addFilter(LogFilter(logging.CRITICAL))

        if log_format == "json":
            handler.setFormatter(MultilineJsonFormatter(JSON_FORMAT))
        elif log_format == "simple":
            handler.setFormatter(SimpleFormatter())
        else:
            handler.setFormatter(
                MultilineFormatter(
                    self.critical(
                        CONSOLE_FORMAT.format(
                            colorama.Fore.RED, colorama.Style.BRIGHT, colorama.Style.RESET_ALL
                        )
                    )
                )
            )

        return handler

    def _get_debug_handler(self, log_format):
        handler = logging.StreamHandler(sys.stderr)
        handler.setLevel(logging.DEBUG)
        handler.addFilter(LogFilter(logging.DEBUG))

        if log_format == "json":
            handler.setFormatter(MultilineJsonFormatter(JSON_FORMAT))
        elif log_format == "simple":
            handler.setFormatter(SimpleFormatter())
        else:
            handler.setFormatter(
                MultilineFormatter(
                    self.critical(
                        CONSOLE_FORMAT.format(
                            colorama.Fore.BLUE, colorama.Style.BRIGHT, colorama.Style.RESET_ALL
                        )
                    )
                )
            )

        return handler

    def update_logger(self, level=None, log_level=None):
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)

        self.logger.setLevel(level)
        self.logger.addHandler(self._get_error_handler(log_level))
        self.logger.addHandler(self._get_warning_handler(log_level))
        self.logger.addHandler(self._get_info_handler(log_level))
        self.logger.addHandler(self._get_critical_handler(log_level))
        self.logger.addHandler(self._get_debug_handler(log_level))

    def debug(self, msg):
        """Format info messages and return string."""
        return msg

    def critical(self, msg):
        """Format critical messages and return string."""
        return msg

    def error(self, msg):
        """Format error messages and return string."""
        return msg

    def warning(self, msg):
        """Format warning messages and return string."""
        return msg

    def info(self, msg):
        """Format info messages and return string."""
        return msg

    def _color_text(self, color, msg):
        """
        Colorize strings.

        :param color: colorama color settings
        :param msg: string to colorize
        :returns: string

        """
        return f"{color}{msg}{colorama.Style.RESET_ALL}"

    def sysexit(self, code=1):
        sys.exit(code)

    def sysexit_with_message(self, msg, code=1):
        self.logger.critical(str(msg))
        self.sysexit(code)


class SingleLog(Log, metaclass=Singleton):
    """Singleton logging class."""

    pass
