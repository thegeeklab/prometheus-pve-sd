---
title: Using pip
---

```Shell
# From PyPI as unprivileged user
$ pip install prometheus-pve-sd --user

# .. or as root
$ sudo pip install prometheus-pve-sd

# From Wheel file
$ pip install https://github.com/thegeeklab/prometheus-pve-sd/releases/download/v0.1.0/prometheus_pve_sd-0.1.0-py3-none-any.whl
```

Start the service:

```Shell
prometheus-pve-sd -vv --loop-delay 900 -o /etc/prometheus/pve.json
```

After configuring and starting the service, Prometheus need to be [configured](/usage/getting-started/#prometheus-configuration) to use the external service discovery.
