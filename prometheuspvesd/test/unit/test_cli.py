"""Test CLI class."""

import json

import pytest
from proxmoxer import ProxmoxAPI

import prometheuspvesd.exception
from prometheuspvesd.cli import PrometheusSD
from prometheuspvesd.client import ProxmoxClient
from prometheuspvesd.config import Config
from prometheuspvesd.discovery import Discovery
from prometheuspvesd.exception import APIError
from prometheuspvesd.logger import Log

pytest_plugins = [
    "prometheuspvesd.test.fixtures.fixtures",
]


def test_cli_required_error(mocker, capsys):
    mocker.patch.object(ProxmoxClient, "_auth", return_value=mocker.create_autospec(ProxmoxAPI))
    mocker.patch.object(PrometheusSD, "_fetch", return_value=True)

    with pytest.raises(SystemExit) as e:
        PrometheusSD()

    stdout, stderr = capsys.readouterr()
    assert "Option 'pve.server' is required but not set" in stderr
    assert e.value.code == 1


@pytest.mark.parametrize(
    "testinput",
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
def test_cli_auth_required_error(mocker, capsys, builtins, testinput):
    for key, value in testinput.items():
        builtins[key]["default"] = value

    mocker.patch.dict(Config.SETTINGS, builtins)
    mocker.patch.object(ProxmoxClient, "_auth", return_value=mocker.create_autospec(ProxmoxAPI))
    mocker.patch.object(PrometheusSD, "_fetch", return_value=True)

    with pytest.raises(SystemExit) as e:
        PrometheusSD()

    stdout, stderr = capsys.readouterr()
    assert (
        "Either 'pve.password' or 'pve.token_name' and 'pve.token_value' are required but not set"
        in stderr
    )
    assert e.value.code == 1


@pytest.mark.parametrize(
    "testinput",
    [
        {"pve.password": "dummy", "pve.token_name": "", "pve.token_value": ""},
        {"pve.password": "", "pve.token_name": "dummy", "pve.token_value": "dummy"},
    ],
)
def test_cli_auth_no_error(mocker, builtins, testinput):
    for key, value in testinput.items():
        builtins[key]["default"] = value

    mocker.patch.dict(Config.SETTINGS, builtins)
    mocker.patch.object(ProxmoxClient, "_auth", return_value=mocker.create_autospec(ProxmoxAPI))
    mocker.patch.object(PrometheusSD, "_fetch", return_value=True)

    psd = PrometheusSD()

    for key, value in testinput.items():
        assert psd.config.config["pve"][key.split(".")[1]] == value


def test_cli_config_error(mocker, capsys):
    mocker.patch(
        "prometheuspvesd.config.SingleConfig.__init__",
        side_effect=prometheuspvesd.exception.ConfigError("Dummy Config Exception"),
    )
    mocker.patch.object(ProxmoxClient, "_auth", return_value=mocker.create_autospec(ProxmoxAPI))
    mocker.patch.object(PrometheusSD, "_fetch", return_value=True)

    with pytest.raises(SystemExit) as e:
        PrometheusSD()

    stdout, stderr = capsys.readouterr()
    assert "Dummy Config Exception" in stderr
    assert e.value.code == 1


def test_cli_log_error(mocker, capsys):
    mocker.patch.object(Log, "update_logger", side_effect=ValueError("Dummy Loglevel Exception"))
    mocker.patch.object(ProxmoxClient, "_auth", return_value=mocker.create_autospec(ProxmoxAPI))
    mocker.patch.object(PrometheusSD, "_fetch", return_value=True)

    with pytest.raises(SystemExit) as e:
        PrometheusSD()

    stdout, stderr = capsys.readouterr()
    assert "Dummy Loglevel Exception" in stderr
    assert e.value.code == 1


def test_cli_api_error(mocker, builtins, capsys):
    mocker.patch.dict(Config.SETTINGS, builtins)
    mocker.patch.object(ProxmoxClient, "_auth", side_effect=APIError("Dummy API Exception"))
    mocker.patch.object(PrometheusSD, "_fetch", return_value=True)

    with pytest.raises(SystemExit) as e:
        PrometheusSD()

    stdout, stderr = capsys.readouterr()
    assert "Proxmoxer API error: Dummy API Exception" in stderr
    assert e.value.code == 1


def test_cli_write(mocker, tmp_path, builtins, inventory, labels):
    temp = tmp_path / "temp.txt"
    out = tmp_path / "out.txt"

    builtins["output_file"]["default"] = out.as_posix()

    mocker.patch.dict(Config.SETTINGS, builtins)
    mocker.patch.object(ProxmoxClient, "_auth", return_value=mocker.create_autospec(ProxmoxAPI))
    mocker.patch.object(Discovery, "propagate", return_value=inventory)
    mocker.patch("tempfile.NamedTemporaryFile", return_value=temp.open("w"))

    psd = PrometheusSD()
    assert json.loads(out.read_text()) == labels
    assert oct(out.stat().st_mode & 0o777) == oct(int(psd.config.config["output_file_mode"], 8))
