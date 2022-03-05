"""Test CLI class."""
import os
import pytest

from proxmoxer import ProxmoxAPI

from prometheuspvesd.cli import PrometheusSD
from prometheuspvesd.discovery import Discovery
from prometheuspvesd.exception import APIError
from prometheuspvesd.config import Config

pytest_plugins = [
    "prometheuspvesd.test.fixtures.fixtures",
]


def test_cli_args(mocker, environment, defaults):
    mocker.patch.dict(os.environ, environment)
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


def test_cli_config_error(mocker, environment, defaults):
    mocker.patch.dict(os.environ, environment)
    mocker.patch(
        "sys.argv", [
            "prometheus-pve-sd",
            "-c",
            "./prometheuspvesd/test/data/config.yml",
        ]
    )

    mocker.patch.object(Discovery, "_auth", return_value=mocker.create_autospec(ProxmoxAPI))
    mocker.patch.object(PrometheusSD, "_fetch", return_value=True)

    with pytest.raises(SystemExit) as e:
        PrometheusSD()

    assert e.value.code == 1


def test_cli_api_error(mocker, environment, defaults):
    mocker.patch.dict(os.environ, environment)
    mocker.patch.dict(Config.SETTINGS, {"service": {"default": False}})

    mocker.patch.object(Discovery, "_auth", side_effect=APIError("Dummy API Exception"))
    mocker.patch.object(PrometheusSD, "_fetch", return_value=True)

    with pytest.raises(SystemExit) as e:
        PrometheusSD()

    assert e.value.code == 1
