#!/usr/bin/env python3
"""Prometheus SD object models."""

from typing import Any


class Host:
    """Represents a virtual machine or container in PVE."""

    def __init__(
        self,
        vmid: str,
        hostname: str,
        ipv4_address: str | None,
        ipv6_address: str | None,
        pve_type: str,
    ) -> None:
        self.hostname = str(hostname)
        self.ipv4_address = str(ipv4_address) if ipv4_address else None
        self.ipv6_address = str(ipv6_address) if ipv6_address else None
        self.vmid = str(vmid)
        self.pve_type = str(pve_type)
        self.labels: dict[str, str] = {}
        self.add_label("ipv4", ipv4_address)
        self.add_label("ipv6", ipv6_address)
        self.add_label("name", hostname)
        self.add_label("type", pve_type)
        self.add_label("vmid", vmid)

    def __str__(self) -> str:
        ipv4 = self.ipv4_address if self.ipv4_address is not None else "False"
        ipv6 = self.ipv6_address if self.ipv6_address is not None else "False"
        return f"{self.hostname}({self.vmid}): {self.pve_type} {ipv4} {ipv6}"

    def add_label(self, key: str, value: Any) -> None:
        key = key.replace("-", "_").replace(" ", "_")
        self.labels[f"__meta_pve_{key}"] = str(value) if value is not None else "False"

    def to_sd_json(self) -> dict[str, Any]:
        return {"targets": [self.hostname], "labels": self.labels}


class HostList:
    """Collection of host objects."""

    def __init__(self) -> None:
        self.hosts: list[Host] = []

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, HostList):
            return False

        if len(other.hosts) != len(self.hosts):
            return False

        for host in self.hosts:
            if other.host_exists(host):
                continue
            return False

        return True

    def clear(self) -> None:
        self.hosts = []

    def add_host(self, host: Host) -> None:
        if not self.host_exists(host):
            self.hosts.append(host)

    def host_exists(self, host: Host) -> bool:
        """Check if a host is already in the list by id and type."""
        for current in self.hosts:
            if current.pve_type == host.pve_type and current.vmid == host.vmid:
                return True
        return False
