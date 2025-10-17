#!/usr/bin/env python3
"""Prometheus SD object models."""


class Host:
    """Represents a virtual machine or container in PVE."""

    def __init__(self, vmid, hostname, ipv4_address, ipv6_address, pve_type):
        self.hostname = str(hostname)
        self.ipv4_address = str(ipv4_address)
        self.ipv6_address = str(ipv6_address)
        self.vmid = str(vmid)
        self.pve_type = str(pve_type)
        self.labels = {}
        self.add_label("ipv4", ipv4_address)
        self.add_label("ipv6", ipv6_address)
        self.add_label("name", hostname)
        self.add_label("type", pve_type)
        self.add_label("vmid", vmid)

    def __str__(self):
        return (
            f"{self.hostname}({self.vmid}): "
            f"{self.pve_type} {self.ipv4_address} {self.ipv6_address}"
        )

    def add_label(self, key, value):
        key = key.replace("-", "_").replace(" ", "_")
        self.labels[f"__meta_pve_{key}"] = str(value)

    def to_sd_json(self):
        return {"targets": [self.hostname], "labels": self.labels}
    
    def is_same_config(self, other):
        return (
            self.hostname == other.hostname and
            self.ipv4_address == other.ipv4_address and
            self.ipv6_address == other.ipv6_address and
            self.pve_type == other.pve_type and
            self.vmid == other.vmid
        )


class HostList:
    """Collection of host objects."""

    def __init__(self):
        self.hosts = []

    def __eq__(self, other):
        if not isinstance(other, HostList):
            return False

        if len(other.hosts) != len(self.hosts):
            return False

        for host in self.hosts:
            if other.host_exists(host):
                continue
            return False

        self_hosts_by_name = {host.hostname: host for host in self.hosts}
        other_hosts_by_name = {host.hostname: host for host in other.hosts}

        if set(self_hosts_by_name.keys()) != set(other_hosts_by_name.keys()):
            return False

        for name, host in self_hosts_by_name.items():
            if not host.is_same_config(other_hosts_by_name[name]):
                return False

        return True

    def clear(self):
        self.hosts = []

    def add_host(self, host: Host):
        existing_index = None
        for i, existing_host in enumerate(self.hosts):
            if existing_host.pve_type == host.pve_type and existing_host.vmid == host.vmid:
                existing_index = i
                break
        
        if existing_index is not None:
            existing_host = self.hosts[existing_index]
            if not existing_host.is_same_config(host):
                self.hosts[existing_index] = host
                return
            else:
                return
        
        self.hosts.append(host)

    def host_exists(self, host: Host):
        """Check if a host is already in the list by id and type."""
        for current in self.hosts:
            if current.pve_type == host.pve_type and current.vmid == host.vmid:
                return True
        return False
