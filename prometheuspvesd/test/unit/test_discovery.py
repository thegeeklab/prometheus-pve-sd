"""Test Discovery class."""
from unittest.mock import MagicMock

import pytest
from proxmoxer import ProxmoxAPI

from prometheuspvesd.client import ProxmoxClient
from prometheuspvesd.discovery import Discovery

pytest_plugins = [
    "prometheuspvesd.test.fixtures.fixtures",
]


@pytest.fixture
def discovery(mocker):
    mocker.patch.object(ProxmoxClient, "_auth", return_value=mocker.create_autospec(ProxmoxAPI))

    return Discovery()


def test_exclude_vmid(discovery, qemus):
    discovery.config.config["exclude_vmid"] = ["100", "101", "102"]
    filtered = discovery._filter(qemus)

    assert len(filtered) == 0


def test_exclude_state(discovery, qemus):
    discovery.config.config["exclude_state"] = ["prelaunch"]
    filtered = discovery._filter(qemus)

    assert len(filtered) == 2


def test_exclude_tags(discovery, qemus):
    discovery.config.config["exclude_tags"] = ["unmonitored"]
    filtered = discovery._filter(qemus)

    assert len(filtered) == 2


@pytest.mark.parametrize(
    "testinput,expected", [
        (["monitored"], 1),
        (["monitored", "postgres"], 2),
        ([], 3),
    ]
)
def test_include_tags(discovery, qemus, testinput, expected):
    discovery.config.config["include_tags"] = testinput
    filtered = discovery._filter(qemus)

    assert len(filtered) == expected


@pytest.mark.parametrize("testinput,expected", [
    (["101", "100"], 2),
    ([], 3),
])
def test_include_vmid(discovery, qemus, testinput, expected):
    discovery.config.config["include_vmid"] = testinput
    filtered = discovery._filter(qemus)

    assert len(filtered) == expected


def test_include_and_exclude_tags(discovery, qemus):
    discovery.config.config["include_tags"] = ["postgres"]
    discovery.config.config["exclude_tags"] = ["unmonitored"]
    filtered = discovery._filter(qemus)

    assert len(filtered) == 0


def test_validate_ip(discovery, addresses):
    # IPv4 validation
    for address in addresses["ipv4_valid"]:
        assert discovery._validate_ip(address)
    for address in addresses["ipv4_invalid"]:
        assert not discovery._validate_ip(address)

    # IPv6 validation
    for address in addresses["ipv6_valid"]:
        assert discovery._validate_ip(address)
    for address in addresses["ipv6_invalid"]:
        assert not discovery._validate_ip(address)


def test_get_ip_addresses(discovery, networks):
    discovery.client.get_network_interfaces = MagicMock(return_value=networks)

    assert discovery._get_ip_addresses("qemu", "dummy", "dummy") == (
        networks[1]["ip-addresses"][0]["ip-address"],
        networks[1]["ip-addresses"][2]["ip-address"],
    )
