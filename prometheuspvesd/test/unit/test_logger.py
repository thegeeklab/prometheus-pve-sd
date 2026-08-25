"""Test Log class and formatters."""

import json
import logging
import uuid

import pytest
from _pytest.capture import CaptureFixture
from colorama import Fore, Style

from prometheuspvesd.logger import JSON_FORMAT, ConsoleFormatter, Log, MultilineJsonFormatter

RESET = Style.RESET_ALL


def _make_log(log_format: str = "console", level: int = logging.DEBUG) -> Log:
    return Log(level=level, name=f"test-{uuid.uuid4().hex}", log_format=log_format)


@pytest.mark.parametrize(
    "level,color,stream",
    [
        (logging.DEBUG, Fore.BLUE, "stderr"),
        (logging.INFO, Fore.CYAN, "stdout"),
        (logging.WARNING, Fore.YELLOW, "stdout"),
        (logging.ERROR, Fore.RED, "stderr"),
        (logging.CRITICAL, Fore.RED, "stderr"),
    ],
    ids=["debug", "info", "warning", "error", "critical"],
)
def test_console_format_and_colors(
    capsys: CaptureFixture[str], level: int, color: str, stream: str
) -> None:
    log = _make_log("console")
    log.logger.log(level, "hello")

    out, err = capsys.readouterr()
    expected = f"{color}{Style.BRIGHT}[{logging.getLevelName(level)}]{RESET} hello\n"

    if stream == "stdout":
        assert (out, err) == (expected, "")
    else:
        assert (out, err) == ("", expected)


def test_console_multiline_resets_color(capsys: CaptureFixture[str]) -> None:
    log = _make_log("console")
    log.logger.error("line1\nline2")

    _, err = capsys.readouterr()

    assert err == f"{Fore.RED}{Style.BRIGHT}[ERROR]{RESET} line1\n{RESET}... line2\n"


def test_simple_format(capsys: CaptureFixture[str]) -> None:
    log = _make_log("simple")
    log.logger.info("just a message")

    out, _ = capsys.readouterr()

    assert out == "just a message\n"


def test_json_format(capsys: CaptureFixture[str]) -> None:
    log = _make_log("json")
    log.logger.warning("json msg")

    out, _ = capsys.readouterr()

    record = json.loads(out)
    assert record["levelname"] == "WARNING"
    assert record["message"] == "json msg"
    assert "asctime" in record


def test_json_multiline_replaces_newlines(capsys: CaptureFixture[str]) -> None:
    log = _make_log("json")
    log.logger.warning("line1\nline2")

    out, _ = capsys.readouterr()

    assert json.loads(out)["message"] == "line1 line2"


def test_log_level_is_respected(capsys: CaptureFixture[str]) -> None:
    log = _make_log("console", level=logging.ERROR)
    log.logger.warning("w")
    log.logger.error("e")

    out, err = capsys.readouterr()

    assert "w" not in out
    assert "e" in err


def test_update_logger_reconfigures_level_and_format(capsys: CaptureFixture[str]) -> None:
    log = _make_log("console", level=logging.WARNING)
    log.logger.debug("hidden")
    out, err = capsys.readouterr()
    assert "hidden" not in out and "hidden" not in err

    log.update_logger(logging.DEBUG, "simple")
    log.logger.debug("shown")

    _, err = capsys.readouterr()
    assert err == "shown\n"


@pytest.mark.parametrize(
    "formatter",
    [ConsoleFormatter(), MultilineJsonFormatter(JSON_FORMAT)],
    ids=["console", "json"],
)
def test_formatter_does_not_mutate_record(formatter: logging.Formatter) -> None:
    record = logging.LogRecord("test", logging.ERROR, "", 0, "a\nb", None, None)

    formatter.format(record)

    assert record.msg == "a\nb"
