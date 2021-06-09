#!/usr/bin/env python3
"""Entrypoint and CLI handler."""

import argparse
import json
import shutil
import signal
import tempfile
from time import sleep

import prometheuspvesd.exception
from prometheuspvesd import __version__
from prometheuspvesd.config import SingleConfig
from prometheuspvesd.discovery import Discovery
from prometheuspvesd.model import HostList
from prometheuspvesd.utils import SingleLog


class PrometheusSD:
    """Main Prometheus SD object."""

    def __init__(self):
        self.log = SingleLog()
        self.logger = self.log.logger
        self.args = self._cli_args()
        self.config = self._get_config()

        self.discovery = Discovery()
        self._fetch()

    def _cli_args(self):
        """
        Use argparse for parsing CLI arguments.

        :return: args objec
        """
        parser = argparse.ArgumentParser(description="Prometheus Service Discovery for Proxmox VE")
        parser.add_argument(
            "-c", "--config", dest="config_file", help="location of configuration file"
        )
        parser.add_argument(
            "-o", "--output", dest="output_file", action="store", help="output file"
        )
        parser.add_argument(
            "-d",
            "--loop-delay",
            dest="loop_delay",
            action="store",
            help="delay between discovery runs"
        )
        parser.add_argument(
            "--no-service",
            dest="service",
            action="store_false",
            help="run discovery as a service"
        )
        parser.add_argument(
            "-v", dest="logging.level", action="append_const", const=-1, help="increase log level"
        )
        parser.add_argument(
            "-q", dest="logging.level", action="append_const", const=1, help="decrease log level"
        )
        parser.add_argument(
            "--version", action="version", version="%(prog)s {}".format(__version__)
        )

        return parser.parse_args().__dict__

    def _get_config(self):
        try:
            config = SingleConfig(args=self.args)
        except prometheuspvesd.exception.ConfigError as e:
            self.log.sysexit_with_message(e)

        try:
            self.log.set_level(config.config["logging"]["level"])
        except ValueError as e:
            self.log.sysexit_with_message("Can not set log level.\n{}".format(str(e)))

        required = [("pve.server", config.config["pve"]["server"]),
                    ("pve.user", config.config["pve"]["user"]),
                    ("pve.password", config.config["pve"]["password"])]
        for name, value in required:
            if not value:
                self.log.sysexit_with_message("Option '{}' is required but not set".format(name))

        self.logger.info("Using config file {}".format(config.config_file))

        return config

    def _fetch(self):
        signal.signal(signal.SIGINT, self._terminate)
        signal.signal(signal.SIGTERM, self._terminate)

        loop_delay = self.config.config["loop_delay"]
        output_file = self.config.config["output_file"]

        self.logger.info("Writes targets to {}".format(output_file))
        self.logger.debug("Propagate from PVE")

        while True:
            self._write(self.discovery.propagate())

            if not self.config.config["service"]:
                break

            self.logger.info("Waiting {} seconds for next discovery loop".format(loop_delay))
            sleep(self.config.config["loop_delay"])

    def _write(self, host_list: HostList):
        output = []
        for host in host_list.hosts:
            output.append(host.to_sd_json())

        # Write to tmp file and move after write
        temp_file = tempfile.NamedTemporaryFile(mode="w", prefix="prometheus-pve-sd", delete=False)
        with temp_file as tf:
            json.dump(output, tf, indent=4)

        shutil.move(temp_file.name, self.config.config["output_file"])

    def _terminate(self, signal, frame):
        self.log.sysexit_with_message("Terminating", code=0)


def main():
    PrometheusSD()
