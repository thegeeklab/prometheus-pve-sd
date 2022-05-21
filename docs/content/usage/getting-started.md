---
title: Getting Started
---

{{< toc >}}

## Available Labels

The following list of meta labels can be used to relabel your scrape results:

`__meta_pve_ipv4`
: Discovered IPv4 address or `False` if not found. To discover the IP address either QEMU guest agent or a cloud-init configuration is required.

`__meta_pve_ipv6`
: Discovered IPv6 address or `False` if not found. To discover the IP address either QEMU guest agent or a cloud-init configuration is required.

`__meta_pve_name`
: Name of the node.

`__meta_pve_type`
: Node type, either `qemu` or `lxc`.

`__meta_pve_vmid`
: VMID of the node.

`__meta_pve_cpu`
: Current CPU load of the node.

`__meta_pve_cores`
: Assigned CPU cores for the node.

`__meta_pve_memory`
: Assigned RAM for the node.

`__meta_pve_status`
: Current state of the node.

`__meta_pve_tags`
: A comma-separated list of tags, as set on the node. The label is not getting exported if no tags were found. (Requires PVE 6+)

`__meta_pve_groups`
: Groups discovered from the `Notes` field of the node. Need to be a valid JSON string e.g. `{"groups":["group1","group2"]}`.

## Prometheus configuration

### File service discovery

Prometheus needs a basic file service discovery configuration to fetch system metrics from the host's discovered from PVE. Depending on the used metrics exporter the configuration need to be adjusted, using [Telegraf](https://github.com/influxdata/telegraf/) a starter configuration might look like this:

```YAML
- file_sd_configs:
  - files:
    - /opt/prometheus/conf/file_sd/proxmox.json
  job_name: telegraf-pve
  metrics_path: /metrics
  relabel_configs:
  - replacement: ${1}:9273
    source_labels:
    - __meta_pve_name
    target_label: __address__
  - source_labels:
    - __meta_pve_name
    target_label: instance
```

### HTTP service discovery

If the static file is served by a web server, e.g. while using the [Prometheus Operator](/setup/prometheus-operator/) setup, a HTTP service discovery configuration is required:

```YAML
- http_sd_configs:
    - url: http://pve-sd-service:80/proxmox.json
  job_name: telegraf-pve
  metrics_path: /metrics
  relabel_configs:
  - replacement: ${1}:9273
    source_labels:
    - __meta_pve_name
    target_label: __address__
  - source_labels:
    - __meta_pve_name
    target_label: instance
```
