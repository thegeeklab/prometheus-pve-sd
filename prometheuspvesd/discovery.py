#!/usr/bin/env python3
"""Prometheus Discovery."""

import json
import re
import socket
from collections import defaultdict

import requests

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

    def _get_ip_address(self, pve_type, pve_node, vmid):

        def validate(address):
            try:
                # IP address validation
                if socket.inet_aton(address):
                    # Ignore localhost
                    if address != "127.0.0.1":
                        return address
            except socket.error:
                return False

        address = False
        networks = False
        if pve_type == "qemu":
            # If qemu agent is enabled, try to gather the IP address
            try:
                if self.client.nodes(pve_node).get(pve_type, vmid, "agent", "info") is not None:
                    networks = self.client.nodes(pve_node).get(
                        "qemu", vmid, "agent", "network-get-interfaces"
                    )["result"]
            except Exception:  # noqa  # nosec
                pass

            if networks:
                if type(networks) is list:
                    for network in networks:
                        for ip_address in network["ip-addresses"]:
                            address = validate(ip_address["ip-address"])

        if not address:
            try:
                config = self.client.nodes(pve_node).get(pve_type, vmid, "config")
                sources = [config["net0"], config["ipconfig0"]]

                for s in sources:
                    find = re.search(r"ip=(\d*\.\d*\.\d*\.\d*)", str(sources))
                    if find and find.group(1):
                        address = find.group(1)
                        break
            except Exception:  # noqa  # nosec
                pass

        return address

    def _exclude(self, pve_list):
        filtered = []
        for item in pve_list:
            obj = defaultdict(dict, item)
            if obj["template"] == 1:
                continue

            if obj["status"] in map(str, self.config.config["exclude_state"]):
                continue

            if obj["vmid"] in map(str, self.config.config["exclude_vmid"]):
                continue

            filtered.append(item.copy())
        return filtered

    def propagate(self):
        self.host_list.clear()

        for node in self._get_names(self.client.nodes.get(), "node"):
            try:
                qemu_list = self._exclude(self.client.nodes(node).qemu.get())
                container_list = self._exclude(self.client.nodes(node).lxc.get())
            except Exception as e:  # noqa
                raise APIError(str(e))

            # Merge QEMU and Containers lists from this node
            instances = self._get_variables(qemu_list, "qemu").copy()
            instances.update(self._get_variables(container_list, "container"))

            self.logger.info("Found {} targets".format(len(instances)))
            for host in instances:
                host_meta = instances[host]
                vmid = host_meta["proxmox_vmid"]

                try:
                    pve_type = host_meta["proxmox_type"]
                except KeyError:
                    pve_type = "qemu"

                config = self.client.nodes(node).get(pve_type, vmid, "config")

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

                address = self._get_ip_address(pve_type, node, vmid) or host

                prom_host = Host(vmid, host, address, pve_type)

                config_flags = [("cpu", "sockets"), ("cores", "cores"), ("memory", "memory")]
                meta_flags = [("status", "proxmox_status")]

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
