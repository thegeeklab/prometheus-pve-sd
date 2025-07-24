"""Test Discovery class."""

import logging

import pytest
from proxmoxer import ProxmoxAPI

from prometheuspvesd.client import ProxmoxClient
from prometheuspvesd.discovery import Discovery

pytest_plugins = [
    "prometheuspvesd.test.fixtures.fixtures",
]


def records_to_messages(records):
    return [r.getMessage() for r in records]


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


def test_exclude_tags(discovery, qemus, local_caplog):
    discovery.config.config["exclude_tags"] = ["unmonitored"]

    with local_caplog(level=logging.DEBUG) as caplog:
        filtered = discovery._filter(qemus)

    assert (
        "vmid 100: discovered tags: ['unmonitored', 'excluded', 'postgres']"
        in records_to_messages(caplog.records)
    )
    assert "vmid 100: excluded by tags: ['unmonitored']"
    assert len(filtered) == 2


@pytest.mark.parametrize(
    "testinput,expected",
    [
        (["monitored"], 1),
        (["monitored", "postgres"], 2),
        ([], 3),
    ],
)
def test_include_tags(discovery, qemus, testinput, expected):
    discovery.config.config["include_tags"] = testinput
    filtered = discovery._filter(qemus)

    assert len(filtered) == expected


@pytest.mark.parametrize(
    "testinput,expected",
    [
        (["101", "100"], 2),
        ([], 3),
    ],
)
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


def test_get_ip_addresses(mocker, discovery, networks):
    mocker.patch.object(ProxmoxClient, "get_network_interfaces", return_value=networks)

    assert discovery._get_ip_addresses("qemu", "dummy", "dummy") == (
        networks[1]["ip-addresses"][0]["ip-address"],
        networks[1]["ip-addresses"][2]["ip-address"],
    )


def test_get_ip_addresses_from_instance_config(mocker, discovery, instance_config):
    mocker.patch.object(ProxmoxClient, "get_network_interfaces", return_value=[])
    mocker.patch.object(ProxmoxClient, "get_instance_config", return_value=instance_config)

    assert discovery._get_ip_addresses("qemu", "dummy", "dummy") == (
        "192.0.2.25",
        "2001:db8::666:77:8888",
    )


def test_propagate(
    mocker, discovery, nodes, qemus, instance_config, agent_info, networks, inventory
):
    mocker.patch.object(ProxmoxClient, "get_nodes", return_value=nodes)
    mocker.patch.object(ProxmoxClient, "get_all_vms", return_value=qemus)
    mocker.patch.object(ProxmoxClient, "get_instance_config", return_value=instance_config)
    mocker.patch.object(ProxmoxClient, "get_agent_info", return_value=agent_info)
    mocker.patch.object(ProxmoxClient, "get_network_interfaces", return_value=networks)

    assert discovery.propagate() == inventory


def test_duplicate_vm_names(mocker, discovery, nodes, qemus, agent_info, networks):
    """Test that VMs with duplicate names are handled correctly using vmid as key."""
    # Create duplicate names by modifying the existing qemus fixture
    duplicate_name_vms = [vm.copy() for vm in qemus]
    for vm in duplicate_name_vms:
        vm["name"] = "gitlab-runner"  # Give all VMs the same name

    instance_config = {
        "name": "gitlab-runner",
        "description": "{}",
        "cpu": 2,
        "cores": 2,
    }

    mocker.patch.object(ProxmoxClient, "get_nodes", return_value=nodes)
    mocker.patch.object(ProxmoxClient, "get_all_vms", return_value=duplicate_name_vms)
    mocker.patch.object(ProxmoxClient, "get_all_containers", return_value=[])
    mocker.patch.object(ProxmoxClient, "get_instance_config", return_value=instance_config)
    mocker.patch.object(ProxmoxClient, "get_agent_info", return_value=agent_info)
    mocker.patch.object(ProxmoxClient, "get_network_interfaces", return_value=networks)

    result = discovery.propagate()

    # All VMs should be present in the result (3 from qemus fixture)
    assert len(result.hosts) == 3

    # All should have the same name but different vmids
    vmids = [host.vmid for host in result.hosts]
    hostnames = [host.hostname for host in result.hosts]

    assert "100" in vmids
    assert "101" in vmids
    assert "102" in vmids
    assert hostnames.count("gitlab-runner") == 3
