"""Test CLI class."""
import pytest
from proxmoxer import ProxmoxAPI

from prometheuspvesd.cli import PrometheusSD
from prometheuspvesd.config import Config
from prometheuspvesd.discovery import Discovery
from prometheuspvesd.exception import APIError

pytest_plugins = [
    "prometheuspvesd.test.fixtures.fixtures",
]


def test_cli_args(mocker, builtins, defaults):
    mocker.patch.dict(Config.SETTINGS, builtins)
    mocker.patch("sys.argv", [
        "prometheus-pve-sd",
        "--no-service",
        "-vvv",
    ])

    mocker.patch.object(Discovery, "_auth", return_value=mocker.create_autospec(ProxmoxAPI))
    mocker.patch.object(PrometheusSD, "_fetch", return_value=True)

    pve = PrometheusSD()
    defaults["service"] = False
    defaults["logging"]["level"] = "DEBUG"

    assert pve.config.config == defaults


def test_cli_config_error(mocker, capsys):
    mocker.patch.object(Discovery, "_auth", return_value=mocker.create_autospec(ProxmoxAPI))
    mocker.patch.object(PrometheusSD, "_fetch", return_value=True)

    with pytest.raises(SystemExit) as e:
        PrometheusSD()

    stdout, stderr = capsys.readouterr()
    assert "Option 'pve.server' is required but not set" in stderr
    assert e.value.code == 1


def test_cli_api_error(mocker, builtins, capsys):
    mocker.patch.dict(Config.SETTINGS, builtins)
    mocker.patch.object(Discovery, "_auth", side_effect=APIError("Dummy API Exception"))
    mocker.patch.object(PrometheusSD, "_fetch", return_value=True)

    with pytest.raises(SystemExit) as e:
        PrometheusSD()

    stdout, stderr = capsys.readouterr()
    assert "Proxmoxer API error: Dummy API Exception" in stderr
    assert e.value.code == 1
