"""Proxmox Client."""

import requests
from prometheus_client import Counter

from prometheuspvesd.config import SingleConfig
from prometheuspvesd.exception import APIError
from prometheuspvesd.logger import SingleLog
from prometheuspvesd.model import HostList
from prometheuspvesd.utils import to_bool

try:
    from proxmoxer import ProxmoxAPI

    HAS_PROXMOXER = True
except ImportError:
    HAS_PROXMOXER = False

PVE_REQUEST_COUNT_TOTAL = Counter("pve_sd_requests_total", "Total count of requests to PVE API")
PVE_REQUEST_COUNT_ERROR_TOTAL = Counter(
    "pve_sd_requests_error_total", "Total count of failed requests to PVE API"
)


class ProxmoxClient:
    """Proxmox API Client."""

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
        self.logger.debug("Successfully authenticated")
        self.host_list = HostList()

    def _auth(self):
        try:
            self.logger.debug(
                "Trying to authenticate against {} as user {}".format(
                    self.config.config["pve"]["server"], self.config.config["pve"]["user"]
                )
            )

            if self.config.config["pve"]["token_name"]:
                self.logger.debug("Using token login")
                return ProxmoxAPI(
                    self.config.config["pve"]["server"],
                    user=self.config.config["pve"]["user"],
                    token_name=self.config.config["pve"]["token_name"],
                    token_value=self.config.config["pve"]["token_value"],
                    verify_ssl=to_bool(self.config.config["pve"]["verify_ssl"]),
                    timeout=self.config.config["pve"]["auth_timeout"],
                )

            return ProxmoxAPI(
                self.config.config["pve"]["server"],
                user=self.config.config["pve"]["user"],
                password=self.config.config["pve"]["password"],
                verify_ssl=to_bool(self.config.config["pve"]["verify_ssl"]),
                timeout=self.config.config["pve"]["auth_timeout"],
            )
        except requests.RequestException as e:
            PVE_REQUEST_COUNT_ERROR_TOTAL.inc()
            raise APIError(str(e)) from e

    def _do_request(self, *args):
        PVE_REQUEST_COUNT_TOTAL.inc()
        try:
            # create a new tuple containing nodes and unpack it again for client.get
            return self.client.get(*("nodes", *args))
        except requests.RequestException as e:
            PVE_REQUEST_COUNT_ERROR_TOTAL.inc()
            raise APIError(str(e)) from e

    def get_nodes(self):
        self.logger.debug("fetching all nodes")
        return self._do_request()

    def get_all_vms(self, pve_node):
        self.logger.debug(f"fetching all vms on node {pve_node}")
        return self._do_request(pve_node, "qemu")

    def get_all_containers(self, pve_node):
        self.logger.debug(f"fetching all containers on node {pve_node}")
        return self._do_request(pve_node, "lxc")

    def get_instance_config(self, pve_node, pve_type, vmid):
        self.logger.debug(f"fetching instance config for {vmid} on {pve_node}")
        return self._do_request(pve_node, pve_type, vmid, "config")

    def get_agent_info(self, pve_node, pve_type, vmid):
        self.logger.debug(f"fetching agent info for {vmid} on {pve_node}")
        return self._do_request(pve_node, pve_type, vmid, "agent", "info")["result"]

    def get_network_interfaces(self, pve_node, vmid):
        self.logger.debug(f"fetching network interfaces for {vmid} on {pve_node}")
        return self._do_request(pve_node, "qemu", vmid, "agent", "network-get-interfaces")[
            "result"
        ]
