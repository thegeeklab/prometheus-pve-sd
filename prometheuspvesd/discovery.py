#!/usr/bin/env python3
"""Prometheus Discovery."""

import ipaddress
import json
import re
from collections import defaultdict

import requests
from prometheus_client import Counter
from prometheus_client import Gauge
from prometheus_client import Summary

from prometheuspvesd.config import SingleConfig
from prometheuspvesd.exception import APIError
from prometheuspvesd.logger import SingleLog
from prometheuspvesd.model import Host
from prometheuspvesd.model import HostList
from prometheuspvesd.utils import to_bool

try:
    from proxmoxer import ProxmoxAPI
    HAS_PROXMOXER = True
except ImportError:
    HAS_PROXMOXER = False

PROPAGATION_TIME = Summary(
    "pve_sd_propagate_seconds", "Time spent propagating the inventory from PVE"
)
HOST_GAUGE = Gauge("pve_sd_hosts", "Number of hosts discovered by PVE SD")
PVE_REQUEST_COUNT_TOTAL = Counter("pve_sd_requests_total", "Total count of requests to PVE API")
PVE_REQUEST_COUNT_ERROR_TOTAL = Counter(
    "pve_sd_requests_error_total", "Total count of failed requests to PVE API"
)


class Discovery():
    """Prometheus PVE Service Discovery."""

    def __init__(self):
        if not HAS_PROXMOXER:
            self.log.sysexit_with_message(
                "The Proxmox VE Prometheus SD requires proxmoxer: "
                "https://pypi.org/project/proxmoxer/"
            )

        self.config = SingleConfig()
        self.log = SingleLog()
        self.logger = SingleLog().logger
        self.client = self._auth()
        self.host_list = HostList()

    def _auth(self):
        try:
            return ProxmoxAPI(
                self.config.config["pve"]["server"],
                user=self.config.config["pve"]["user"],
                password=self.config.config["pve"]["password"],
                verify_ssl=to_bool(self.config.config["pve"]["verify_ssl"]),
                timeout=self.config.config["pve"]["auth_timeout"]
            )
        except requests.RequestException as e:
            PVE_REQUEST_COUNT_ERROR_TOTAL.inc()
            raise APIError(str(e))

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
                PVE_REQUEST_COUNT_TOTAL.inc()
                if self.client.get("nodes", pve_node, pve_type, vmid, "agent", "info") is not None:
                    networks = self.client.get(
                        "nodes", pve_node, "qemu", vmid, "agent", "network-get-interfaces"
                    )["result"]
            except Exception:  # noqa  # nosec
                pass

            if type(networks) is list:
                for network in networks:
                    for ip_address in network["ip-addresses"]:
                        if ip_address["ip-address-type"] == "ipv4" and not ipv4_address:
                            ipv4_address = self._validate_ip(ip_address["ip-address"])
                        elif ip_address["ip-address-type"] == "ipv6" and not ipv6_address:
                            ipv6_address = self._validate_ip(ip_address["ip-address"])

        if not ipv4_address:
            try:
                PVE_REQUEST_COUNT_TOTAL.inc()
                config = self.client.get("nodes", pve_node, pve_type, vmid, "config")
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

        if not ipv6_address:
            try:
                PVE_REQUEST_COUNT_TOTAL.inc()
                config = self.client.get("nodes", pve_node, pve_type, vmid, "config")
                if "ipconfig0" in config.keys():
                    sources = [config["net0"], config["ipconfig0"]]
                else:
                    sources = [config["net0"]]

                for s in sources:
                    find = re.search(r"ip=(\d*:\d*:\d*:\d*:\d*:\d*)", str(s))
                    if find and find.group(1):
                        ipv6_address = find.group(1)
                        break
            except Exception:  # noqa  # nosec
                pass

        return ipv4_address, ipv6_address

    def _exclude(self, pve_list):
        filtered = []
        for item in pve_list:
            obj = defaultdict(dict, item)
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

        PVE_REQUEST_COUNT_TOTAL.inc()
        for node in self._get_names(self.client.get("nodes"), "node"):
            try:
                PVE_REQUEST_COUNT_TOTAL.inc()
                qemu_list = self._exclude(self.client.get("nodes", node, "qemu"))
                PVE_REQUEST_COUNT_TOTAL.inc()
                container_list = self._exclude(self.client.get("nodes", node, "lxc"))
            except Exception as e:  # noqa
                PVE_REQUEST_COUNT_ERROR_TOTAL.inc()
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

                PVE_REQUEST_COUNT_TOTAL.inc()
                config = self.client.get("nodes", node, pve_type, vmid, "config")

                try:
                    description = (config["description"])
                except KeyError:
                    description = None
                except Exception as e:  # noqa
                    PVE_REQUEST_COUNT_ERROR_TOTAL.inc()
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
