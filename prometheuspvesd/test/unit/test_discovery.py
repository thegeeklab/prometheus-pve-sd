"""Test Autostop class."""

pytest_plugins = [
    "prometheuspvesd.test.fixtures.fixtures",
]


def get_mock(*args):
    networks = args[0]
    args = args[1:]

    if "info" in args:
        return True
    if "network-get-interfaces" in args:
        return {"result": networks}

    return False


def test_exclude(discovery_fixture, qemus):
    discovery_fixture.config.config["exclude_vmid"] = ["100", "101"]

    expected = []
    filtered = discovery_fixture._exclude(qemus)

    assert filtered == expected


def test_validate_ip(discovery_fixture, addresses):
    # IPv4 validation
    for address in addresses["ipv4_valid"]:
        assert discovery_fixture._validate_ip(address)
    for address in addresses["ipv4_invalid"]:
        assert not discovery_fixture._validate_ip(address)

    # IPv6 validation
    for address in addresses["ipv6_valid"]:
        assert discovery_fixture._validate_ip(address)
    for address in addresses["ipv6_invalid"]:
        assert not discovery_fixture._validate_ip(address)


def test_get_ip_addresses(mocker, discovery_fixture, networks):
    discovery_fixture.client.get.side_effect = lambda *args: get_mock(networks, *args)

    assert discovery_fixture._get_ip_addresses("qemu", "dummy", "dummy") == (
        networks[1]["ip-addresses"][0]["ip-address"],
        networks[1]["ip-addresses"][2]["ip-address"],
    )
