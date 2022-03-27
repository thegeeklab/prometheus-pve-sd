---
title: CLI options
---

You can get all available CLI options by running `prometheus-pve-sd --help`:

```Shell
$ prometheus-pve-sd --help
usage: prometheus-pve-sd [-h] [-c CONFIG_FILE] [-o OUTPUT_FILE] [-m OUTPUT_FILE_MODE] [-d LOOP_DELAY] [--no-service] [-f LOG_FORMAT] [-v] [-q] [--version]

Prometheus Service Discovery for Proxmox VE

options:
  -h, --help            show this help message and exit
  -c CONFIG_FILE, --config CONFIG_FILE
                        location of configuration file
  -o OUTPUT_FILE, --output OUTPUT_FILE
                        output file
  -m OUTPUT_FILE_MODE, --mode OUTPUT_FILE_MODE
                        output file mode
  -d LOOP_DELAY, --loop-delay LOOP_DELAY
                        delay between discovery runs
  --no-service          run discovery only once
  -f LOG_FORMAT, --log-format LOG_FORMAT
                        used log format
  -v                    increase log level
  -q                    decrease log level
  --version             show program's version number and exit
```
