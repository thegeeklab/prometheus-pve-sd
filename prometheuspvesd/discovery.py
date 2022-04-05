#!/usr/bin/env python3
"""Prometheus Discovery."""

import ipaddress
import json
import re
from collections import defaultdict

from prometheus_client import Gauge
from prometheus_client import Summary

from prometheuspvesd.client import ProxmoxClient
from prometheuspvesd.config import SingleConfig
from prometheuspvesd.exception import APIError
from prometheuspvesd.logger import SingleLog
from prometheuspvesd.model import Host
from prometheuspvesd.model import HostList

PROPAGATION_TIME = Summary(
    "pve_sd_propagate_seconds", "Time spent propagating the inventory from PVE"
)
HOST_GAUGE = Gauge("pve_sd_hosts", "Number of hosts discovered by PVE SD")


class Discovery():
    """Prometheus PVE Service Discovery."""

    def __init__(self):
        self.config = SingleConfig()
        self.log = SingleLog()
        self.logger = SingleLog().logger
        self.client = ProxmoxClient()
        self.host_list = HostList()

    def _get_names(self, pve_list, pve_type):
        names = []

        if pve_type == "node":
            names = [node["node"] for node in pve_list]
        elif pve_type == "pool":
            names = [pool["poolid"] for pool in pve_list]

        return names

    def _get_variables(self, pve_list, pve_type):
        variables = {}

        if pve_type in ["qemu", "container"]:
            for vm in pve_list:
                nested = {}
                for key, value in vm.items():
                    nested["proxmox_" + key] = value
                variables[vm["name"]] = nested

        return variables

    def _get_ip_addresses(self, pve_type, pve_node, vmid):
        ipv4_address = False
        ipv6_address = False
        networks = False
        if pve_type == "qemu":
            # If qemu agent is enabled, try to gather the IP address
            try:
                if self.client.get_agent_info(pve_node, pve_type, vmid) is not None:
                    networks = self.client.get_network_interfaces(pve_node, vmid)
            except Exception:  # noqa  # nosec
                pass

            if type(networks) is list:
                for network in networks:
                    for ip_address in network.get("ip-addresses", []):
                        if ip_address["ip-address-type"] == "ipv4" and not ipv4_address:
                            ipv4_address = self._validate_ip(ip_address["ip-address"])
                        elif ip_address["ip-address-type"] == "ipv6" and not ipv6_address:
                            ipv6_address = self._validate_ip(ip_address["ip-address"])

        config = self.client.get_instance_config(pve_node, pve_type, vmid)
        if config and not ipv4_address:
            try:
                if "ipconfig0" in config.keys():
                    sources = [config["net0"], config["ipconfig0"]]
                else:
                    sources = [config["net0"]]

                for s in sources:
                    find = re.search(r"ip=(\d*\.\d*\.\d*\.\d*)", str(s))
                    if find and find.group(1):
                        ipv4_address = find.group(1)
                        break
            except Exception:  # noqa  # nosec
                pass

        if config and not ipv6_address:
            try:
                if "ipconfig0" in config.keys():
                    sources = [config["net0"], config["ipconfig0"]]
                else:
                    sources = [config["net0"]]

                for s in sources:
                    find = re.search(
                        r"ip=(([a-fA-F0-9]{0,4}:{0,2}){0,7}:[0-9a-fA-F]{1,4})", str(s)
                    )
                    if find and find.group(1):
                        ipv6_address = find.group(1)
                        break
            except Exception:  # noqa  # nosec
                pass

        return ipv4_address, ipv6_address

    def _filter(self, pve_list):
        filtered = []
        for item in pve_list:
            obj = defaultdict(dict, item)
            if (
                len(self.config.config["include_vmid"]) > 0
                and str(obj["vmid"]) not in self.config.config["include_vmid"]
            ):
                continue

            if (
                len(self.config.config["include_tags"]) > 0 and (
                    bool(obj["tags"]) is False  # continue if tags is not set
                    or set(obj["tags"].split(",")).isdisjoint(self.config.config["include_tags"])
                )
            ):
                continue

            if obj["template"] == 1:
                continue

            if obj["status"] in map(str, self.config.config["exclude_state"]):
                continue

            if str(obj["vmid"]) in self.config.config["exclude_vmid"]:
                continue

            if (
                isinstance(obj["tags"], str)
                and not set(obj["tags"].split(",")).isdisjoint(self.config.config["exclude_tags"])
            ):
                continue

            filtered.append(item.copy())
        return filtered

    def _validate_ip(self, address: object) -> object:
        try:
            if (
                not ipaddress.ip_address(address).is_loopback
                and not ipaddress.ip_address(address).is_link_local
            ):
                return address
        except ValueError:
            return False

    @PROPAGATION_TIME.time()
    def propagate(self):
        self.host_list.clear()

        for node in self._get_names(self.client.get_nodes(), "node"):
            try:
                qemu_list = self._filter(self.client.get_all_vms(node))
                container_list = self._filter(self.client.get_all_containers(node))
            except Exception as e:  # noqa
                raise APIError(str(e))

            # Merge QEMU and Containers lists from this node
            instances = self._get_variables(qemu_list, "qemu").copy()
            instances.update(self._get_variables(container_list, "container"))

            HOST_GAUGE.set(len(instances))
            self.logger.info("Found {} targets".format(len(instances)))
            for host in instances:
                host_meta = instances[host]
                vmid = host_meta["proxmox_vmid"]

                try:
                    pve_type = host_meta["proxmox_type"]
                except KeyError:
                    pve_type = "qemu"

                config = self.client.get_instance_config(node, pve_type, vmid)

                try:
                    description = (config["description"])
                except KeyError:
                    description = None
                except Exception as e:  # noqa
                    raise APIError(str(e))

                try:
                    metadata = json.loads(description)
                except TypeError:
                    metadata = {}
                except ValueError:
                    metadata = {"notes": description}

                ipv4_address, ipv6_address = self._get_ip_addresses(pve_type, node, vmid)

                prom_host = Host(vmid, host, ipv4_address, ipv6_address, pve_type)

                config_flags = [("cpu", "sockets"), ("cores", "cores"), ("memory", "memory")]
                meta_flags = [("status", "proxmox_status"), ("tags", "proxmox_tags")]

                for key, flag in config_flags:
                    if flag in config:
                        prom_host.add_label(key, config[flag])

                for key, flag in meta_flags:
                    if flag in host_meta:
                        prom_host.add_label(key, host_meta[flag])

                if "groups" in metadata:
                    prom_host.add_label("groups", ",".join(metadata["groups"]))

                self.host_list.add_host(prom_host)
                self.logger.debug("Discovered {}".format(prom_host))

        return self.host_list
