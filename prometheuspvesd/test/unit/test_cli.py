"""Test CLI class."""

import json
import pathlib
from typing import Any

import pytest
from _pytest.capture import CaptureFixture
from proxmoxer import ProxmoxAPI
from pytest_mock import MockerFixture

import prometheuspvesd.exception
from prometheuspvesd.cli import PrometheusSD
from prometheuspvesd.client import ProxmoxClient
from prometheuspvesd.config import Config
from prometheuspvesd.discovery import Discovery
from prometheuspvesd.exception import APIError
from prometheuspvesd.logger import Log
from prometheuspvesd.model import HostList

pytest_plugins = [
    "prometheuspvesd.test.fixtures.fixtures",
]


def test_cli_required_error(mocker: MockerFixture, capsys: CaptureFixture[str]) -> None:
    mocker.patch.object(ProxmoxClient, "_auth", return_value=mocker.create_autospec(ProxmoxAPI))
    mocker.patch.object(PrometheusSD, "_fetch", return_value=True)

    with pytest.raises(SystemExit) as e:
        PrometheusSD()

    _, stderr = capsys.readouterr()
    assert "Option 'pve.server' is required but not set" in stderr
    assert e.value.code == 1


@pytest.mark.parametrize(
    "test_input",
    [
        {"pve.user": "dummy", "pve.password": "", "pve.token_name": "", "pve.token_value": ""},
        {
            "pve.user": "dummy",
            "pve.password": "",
            "pve.token_name": "dummy",
            "pve.token_value": "",
        },
        {
            "pve.user": "dummy",
            "pve.password": "",
            "pve.token_name": "",
            "pve.token_value": "dummy",
        },
    ],
)
def test_cli_auth_required_error(
    mocker: MockerFixture,
    capsys: CaptureFixture[str],
    builtins: dict[str, Any],
    test_input: dict[str, str],
) -> None:
    for key, value in test_input.items():
        builtins[key]["default"] = value

    mocker.patch.dict(Config.SETTINGS, builtins)
    mocker.patch.object(ProxmoxClient, "_auth", return_value=mocker.create_autospec(ProxmoxAPI))
    mocker.patch.object(PrometheusSD, "_fetch", return_value=True)

    with pytest.raises(SystemExit) as e:
        PrometheusSD()

    _, stderr = capsys.readouterr()
    assert (
        "Either 'pve.password' or 'pve.token_name' and 'pve.token_value' are required but not set"
        in stderr
    )
    assert e.value.code == 1


@pytest.mark.parametrize(
    "test_input",
    [
        {"pve.password": "dummy", "pve.token_name": "", "pve.token_value": ""},
        {"pve.password": "", "pve.token_name": "dummy", "pve.token_value": "dummy"},
    ],
)
def test_cli_auth_no_error(
    mocker: MockerFixture, builtins: dict[str, Any], test_input: dict[str, str]
) -> None:
    for key, value in test_input.items():
        builtins[key]["default"] = value

    mocker.patch.dict(Config.SETTINGS, builtins)
    mocker.patch.object(ProxmoxClient, "_auth", return_value=mocker.create_autospec(ProxmoxAPI))
    mocker.patch.object(PrometheusSD, "_fetch", return_value=True)

    psd = PrometheusSD()

    for key, value in test_input.items():
        assert psd.config.config is not None
        assert psd.config.config["pve"][key.split(".")[1]] == value


def test_cli_config_error(mocker: MockerFixture, capsys: CaptureFixture[str]) -> None:
    mocker.patch(
        "prometheuspvesd.config.SingleConfig.__init__",
        side_effect=prometheuspvesd.exception.ConfigError("Dummy Config Exception"),
    )
    mocker.patch.object(ProxmoxClient, "_auth", return_value=mocker.create_autospec(ProxmoxAPI))
    mocker.patch.object(PrometheusSD, "_fetch", return_value=True)

    with pytest.raises(SystemExit) as e:
        PrometheusSD()

    _, stderr = capsys.readouterr()
    assert "Dummy Config Exception" in stderr
    assert e.value.code == 1


def test_cli_log_error(mocker: MockerFixture, capsys: CaptureFixture[str]) -> None:
    mocker.patch.object(Log, "update_logger", side_effect=ValueError("Dummy Loglevel Exception"))
    mocker.patch.object(ProxmoxClient, "_auth", return_value=mocker.create_autospec(ProxmoxAPI))
    mocker.patch.object(PrometheusSD, "_fetch", return_value=True)

    with pytest.raises(SystemExit) as e:
        PrometheusSD()

    _, stderr = capsys.readouterr()
    assert "Dummy Loglevel Exception" in stderr
    assert e.value.code == 1


def test_cli_api_error(
    mocker: MockerFixture, builtins: dict[str, Any], capsys: CaptureFixture[str]
) -> None:
    mocker.patch.dict(Config.SETTINGS, builtins)
    mocker.patch.object(ProxmoxClient, "_auth", side_effect=APIError("Dummy API Exception"))
    mocker.patch.object(PrometheusSD, "_fetch", return_value=True)

    with pytest.raises(SystemExit) as e:
        PrometheusSD()

    _, stderr = capsys.readouterr()
    assert "Proxmoxer API error: Dummy API Exception" in stderr
    assert e.value.code == 1


def test_cli_write(
    mocker: MockerFixture,
    tmp_path: pathlib.Path,
    builtins: dict[str, Any],
    inventory: HostList,
    labels: list[dict[str, Any]],
) -> None:
    temp = tmp_path / "temp.txt"
    out = tmp_path / "out.txt"

    builtins["output_file"]["default"] = out.as_posix()

    mocker.patch.dict(Config.SETTINGS, builtins)
    mocker.patch.object(ProxmoxClient, "_auth", return_value=mocker.create_autospec(ProxmoxAPI))
    mocker.patch.object(Discovery, "propagate", return_value=inventory)
    mocker.patch("tempfile.NamedTemporaryFile", return_value=temp.open("w"))

    psd = PrometheusSD()
    assert psd.config.config is not None
    assert json.loads(out.read_text()) == labels
    assert oct(out.stat().st_mode & 0o777) == oct(int(psd.config.config["output_file_mode"], 8))
