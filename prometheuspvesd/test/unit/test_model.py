"""Test Host class."""
import pytest

from prometheuspvesd.model import Host

pytest_plugins = [
    "prometheuspvesd.test.fixtures.fixtures",
]


@pytest.mark.parametrize(
    "testinput,expected", [
        ({
            "vmid": 101,
            "hostname": "host1",
            "ipv4_address": False,
            "ipv6_address": False,
            "pve_type": "qemu",
        }, {
            "__meta_pve_vmid": "101",
            "__meta_pve_name": "host1",
            "__meta_pve_ipv4": "False",
            "__meta_pve_ipv6": "False",
            "__meta_pve_type": "qemu",
        }),
        ({
            "vmid": "202",
            "hostname": "host2",
            "ipv4_address": "129.168.0.1",
            "ipv6_address": "2001:db8:3333:4444:5555:6666:7777:8888",
            "pve_type": "qemu",
        }, {
            "__meta_pve_vmid": "202",
            "__meta_pve_name": "host2",
            "__meta_pve_ipv4": "129.168.0.1",
            "__meta_pve_ipv6": "2001:db8:3333:4444:5555:6666:7777:8888",
            "__meta_pve_type": "qemu",
        }),
    ]
)
def test_host(testinput, expected):
    host = Host(
        testinput["vmid"],
        testinput["hostname"],
        testinput["ipv4_address"],
        testinput["ipv6_address"],
        testinput["pve_type"],
    )

    assert host.labels == expected
