# prometheus-pve-sd

Prometheus Service Discovery for Proxmox VE

[![Build Status](https://ci.thegeeklab.de/api/badges/thegeeklab/prometheus-pve-sd/status.svg)](https://ci.thegeeklab.de/repos/thegeeklab/prometheus-pve-sd)
[![Docker Hub](https://img.shields.io/badge/dockerhub-latest-blue.svg?logo=docker&logoColor=white)](https://hub.docker.com/r/thegeeklab/prometheus-pve-sd)
[![Quay.io](https://img.shields.io/badge/quay-latest-blue.svg?logo=docker&logoColor=white)](https://quay.io/repository/thegeeklab/prometheus-pve-sd)
[![Python Version](https://img.shields.io/pypi/pyversions/prometheus-pve-sd.svg)](https://pypi.org/project/prometheus-pve-sd/)
[![PyPI Status](https://img.shields.io/pypi/status/prometheus-pve-sd.svg)](https://pypi.org/project/prometheus-pve-sd/)
[![PyPI Release](https://img.shields.io/pypi/v/prometheus-pve-sd.svg)](https://pypi.org/project/prometheus-pve-sd/)
[![GitHub contributors](https://img.shields.io/github/contributors/thegeeklab/prometheus-pve-sd)](https://github.com/thegeeklab/prometheus-pve-sd/graphs/contributors)
[![Source: GitHub](https://img.shields.io/badge/source-github-blue.svg?logo=github&logoColor=white)](https://github.com/thegeeklab/prometheus-pve-sd)
[![License: MIT](https://img.shields.io/github/license/thegeeklab/prometheus-pve-sd)](https://github.com/thegeeklab/prometheus-pve-sd/blob/main/LICENSE)

This project provides a simple custom service discovery for [Prometheus](https://prometheus.io/). It is using the [Proxmox VE](https://www.proxmox.com/de/proxmox-ve) (PVE) API to fetch Hosts and it's meta information to generate a Prometheus compatible [file based](https://prometheus.io/docs/guides/file-sd/) service discovery. Releases are available as Python Packages on [GitHub](https://github.com/thegeeklab/prometheus-pve-sd/releases) or [PyPI](https://pypi.org/project/prometheus-pve-sd/) and as Docker Image on [Docker Hub](https://hub.docker.com/r/thegeeklab/prometheus-pve-sd).

You can find the full documentation at [https://prometheus-pve-sd.geekdocs.de](https://prometheus-pve-sd.geekdocs.de).

## Contributors

Special thanks to all [contributors](https://github.com/thegeeklab/prometheus-pve-sd/graphs/contributors). If you would like to contribute,
please see the [instructions](https://github.com/thegeeklab/prometheus-pve-sd/blob/main/CONTRIBUTING.md).

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/thegeeklab/prometheus-pve-sd/blob/main/LICENSE) file for details.
