#!/usr/bin/env python3
"""Prometheus SD object models."""


class Host:
    """Represents a virtual machine or container in PVE."""

    def __init__(self, vmid, hostname, ipv4_address, ipv6_address, pve_type):
        self.hostname = hostname
        self.ipv4_address = ipv4_address
        self.ipv6_address = ipv6_address
        self.vmid = vmid
        self.pve_type = pve_type
        self.labels = {}
        self.labels["__meta_pve_ipv4"] = ipv4_address
        self.labels["__meta_pve_ipv6"] = ipv6_address
        self.labels["__meta_pve_name"] = hostname
        self.labels["__meta_pve_type"] = pve_type
        self.labels["__meta_pve_vmid"] = str(vmid)

    def __str__(self):
        return f"{self.hostname}({self.vmid}): {self.pve_type} \
                  {self.ipv4_address} {self.ipv6_address}"

    def add_label(self, key, value):
        key = key.replace("-", "_").replace(" ", "_")
        self.labels[f"__meta_pve_{key}"] = str(value)

    def to_sd_json(self):
        return {"targets": [self.hostname], "labels": self.labels}


class HostList:
    """Collection of host objects."""

    def __init__(self):
        self.hosts = []

    def clear(self):
        self.hosts = []

    def add_host(self, host: Host):
        if not self.host_exists(host):
            self.hosts.append(host)

    def host_exists(self, host: Host):
        """Check if a host is already in the list by id and type."""
        for current in self.hosts:
            if current.pve_type == host.pve_type and current.vmid == host.vmid:
                return True
        return False
