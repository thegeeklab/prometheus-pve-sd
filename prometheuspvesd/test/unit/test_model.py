"""Test Host class."""
import pytest

from unittest import TestCase
from prometheuspvesd.model import Host

pytest_plugins = [
    "prometheuspvesd.test.fixtures.fixtures",
]


@pytest.mark.parametrize(
    "testinput,expected", [
        ({
            "vmid": 101,
            "hostname": "host1",
            "ipv4_address": True,
            "ipv6_address": False,
            "pve_type": "qemu",
        }, {
            "__meta_pve_ipv4": "True",
            "__meta_pve_ipv6": "False",
            "__meta_pve_name": "host1",
            "__meta_pve_type": "qemu",
            "__meta_pve_vmid": "101",
        }),
    ]
)
def test_host(mocker, testinput, expected):
    host = Host(
        testinput["vmid"],
        testinput["hostname"],
        testinput["ipv4_address"],
        testinput["ipv6_address"],
        testinput["pve_type"],
    )

    TestCase().assertDictEqual(host.labels, expected)
