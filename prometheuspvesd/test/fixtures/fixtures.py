"""Global pytest fixtures."""

import pytest


@pytest.fixture
def qemus():
    return [
        {
            "diskwrite": 0,
            "vmid": "100",
            "name": "100.example.com",
            "cpu": 0.0202130478509556,
            "diskread": 0,
            "template": "",
            "uptime": 3101505,
            "maxdisk": 26843545600,
            "maxmem": 1073741824,
            "pid": "1765",
            "cpus": 1,
            "netin": 2856071643,
            "disk": 0,
            "status": "running",
            "netout": 12159205236,
            "mem": 496179157,
            "tags": "unmonitored,excluded"
        },
        {
            "diskwrite": 0,
            "vmid": "101",
            "name": "101.example.com",
            "cpu": 0.0202130478509556,
            "diskread": 0,
            "template": "",
            "uptime": 3101505,
            "maxdisk": 26843545600,
            "maxmem": 1073741824,
            "pid": "1765",
            "cpus": 1,
            "netin": 2856071643,
            "disk": 0,
            "status": "running",
            "netout": 12159205236,
            "mem": 496179157
        },
        {
            "diskwrite": 0,
            "vmid": "102",
            "name": "102.example.com",
            "cpu": 0.0202130478509556,
            "diskread": 0,
            "template": "",
            "uptime": 3101505,
            "maxdisk": 26843545600,
            "maxmem": 1073741824,
            "pid": "1765",
            "cpus": 1,
            "netin": 2856071643,
            "disk": 0,
            "status": "prelaunch",
            "netout": 12159205236,
            "mem": 496179157,
            "tags": "monitored"
        },
    ]


@pytest.fixture
def addresses():
    return {
        "ipv4_valid": [
            "192.168.0.1",
            "10.0.0.1",
        ],
        "ipv4_invalid": [
            "127.0.0.1",
            "169.254.1.1",
        ],
        "ipv6_valid": [
            "2001:db8:3333:4444:5555:6666:7777:8888",
            "2001:db8:3333:4444:CCCC:DDDD:EEEE:FFFF",
            "::",
            "2001:db8::",
            "::1234:5678",
            "2001:db8::1234:5678",
            "2001:0db8:0001:0000:0000:0ab9:C0A8:0102",
        ],
        "ipv6_invalid": [
            "::1",
            "fe80::903a:1c1a:e802:11e4",
        ],
    }


@pytest.fixture
def networks():
    return [
        {
            "hardware-address": "00:00:00:00:00:00",
            "ip-addresses": [
                {
                    "ip-address": "127.0.0.1",
                    "ip-address-type": "ipv4",
                    "prefix": 8
                },
                {
                    "ip-address": "::1",
                    "ip-address-type": "ipv6",
                    "prefix": 128
                },
            ],
            "name": "lo",
            "statistics": {
                "rx-bytes": 9280,
                "rx-dropped": 0,
                "rx-errs": 0,
                "rx-packets": 92,
                "tx-bytes": 9280,
                "tx-dropped": 0,
                "tx-errs": 0,
                "tx-packets": 92
            }
        },
        {
            "hardware-address": "92:0b:bd:c1:f8:39",
            "ip-addresses": [
                {
                    "ip-address": "10.168.0.1",
                    "ip-address-type": "ipv4",
                    "prefix": 32
                },
                {
                    "ip-address": "10.168.0.2",
                    "ip-address-type": "ipv4",
                    "prefix": 32
                },
                {
                    "ip-address": "2001:cdba:3333:4444:5555:6666:7777:8888",
                    "ip-address-type": "ipv6",
                    "prefix": 64
                },
            ],
            "name": "eth0",
            "statistics": {
                "rx-bytes": 2861070337,
                "rx-dropped": 0,
                "rx-errs": 0,
                "rx-packets": 18065580,
                "tx-bytes": 12185866619,
                "tx-dropped": 0,
                "tx-errs": 0,
                "tx-packets": 14423878
            }
        },
    ]
