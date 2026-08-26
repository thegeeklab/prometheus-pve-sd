"""Test ProxmoxClient class."""

from typing import Any

import pytest
from proxmoxer.backends.https import Backend
from pytest_mock import MockerFixture

from prometheuspvesd.client import ProxmoxClient
from prometheuspvesd.config import Config

pytest_plugins = [
    "prometheuspvesd.test.fixtures.fixtures",
]


@pytest.mark.parametrize(
    "test_input",
    [
        {"pve.password": "dummy", "pve.token_name": "", "pve.token_value": ""},
        {"pve.password": "", "pve.token_name": "dummy", "pve.token_value": "dummy"},
    ],
)
@pytest.mark.parametrize("server", ["proxmox.example.com", "proxmox.example.com:443", "[::1]:443"])
def test_auth_forwards_server_unchanged(
    mocker: MockerFixture, builtins: dict[str, Any], test_input: dict[str, str], server: str
) -> None:
    """The server value is forwarded unchanged so proxmoxer can parse an optional `:port`."""
    for key, value in test_input.items():
        builtins[key]["default"] = value

    builtins["pve.server"]["default"] = server
    mocker.patch.dict(Config.SETTINGS, builtins)
    mock_proxmox = mocker.patch("prometheuspvesd.client.ProxmoxAPI")

    ProxmoxClient()

    assert mock_proxmox.call_args.args[0] == server
    assert "port" not in mock_proxmox.call_args.kwargs


@pytest.mark.parametrize(
    "host,expected",
    [
        ("proxmox.example.com", "https://proxmox.example.com:8006/api2/json"),
        ("proxmox.example.com:443", "https://proxmox.example.com:443/api2/json"),
        ("[::1]:443", "https://[::1]:443/api2/json"),
    ],
)
def test_proxmoxer_parses_server_port(host: str, expected: str) -> None:
    """Proxmoxer resolves an optional `:port` in the host and falls back to port 8006."""
    auth = {"user": "dummy", "token_name": "dummy", "token_value": "dummy"}

    assert Backend(host=host, **auth).base_url == expected
