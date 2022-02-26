"""Global pytest fixtures."""

import pytest


@pytest.fixture
def qemus():
    return [{
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
        "mem": 496179157
    }, {
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
    }]
