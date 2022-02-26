"""Test Autostop class."""

import pytest
from proxmoxer import ProxmoxAPI

from prometheuspvesd import discovery

pytest_plugins = [
    "prometheuspvesd.test.fixtures.fixtures",
]


@pytest.fixture
def discovery_fixture(mocker):
    mocker.patch.object(
        discovery.Discovery(), "_auth", return_value=mocker.create_autospec(ProxmoxAPI)
    )

    return discovery.Discovery()


def test_exclude(discovery_fixture, qemus):
    discovery_fixture.config.config["exclude_vmid"] = ["100", "101"]

    expected = []
    filtered = discovery_fixture._exclude(qemus)

    assert filtered == expected
