---
title: Getting Started
---

{{< toc >}}

## Start PVE SD

Create a [configuration file](/configuration/defaults/) with the required parameters to connect to your Proxmox VE (PVE) server before you start the service.

```Shell
prometheus-pve-sd -vv --loop-delay 900 -o /etc/prometheus/pve.json
```

## Available Labels

The following list of meta labels can be used to relabel your scrape results:

`__meta_pve_ipv4`
: Discovered IPv4 address or `False` if not found.

`__meta_pve_ipv6`
: Discovered IPv6 address or `False` if not found.

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

Prometheus needs a basic file service discovery configuration to fetch system metrics from the host's discovered from PVE. Depending on the used metrics exporter the configuration need to be adjusted, using [Telegraf](https://github.com/influxdata/telegraf/#telegraf) a starter configuration might look like this:

```YAML
- file_sd_configs:
  - files:
    - /opt/prometheus/conf/file_sd/proxmox.json
  job_name: telegraf-pve
  metrics_path: /metrics
  relabel_configs:
  - replacement: telegraf
    target_label: job
  - replacement: ${1}:9273
    source_labels:
    - __meta_pve_name
    target_label: __address__
  - source_labels:
    - __meta_pve_name
    target_label: instance
```

### Use IP address labels

Instead of `__meta_pve_name`, it is also possible to configure Prometheus to use the address provided by `__meta_pve_ipv4` or `__meta_pve_ipv4` for connections:

```YAML
relabel_configs:
- replacement: ${1}:9273
  source_labels:
  - __meta_pve_ipv4
  target_label: __address__
```

### Convert tags to custom labels

Tags of a node exposed by the `__meta_pve_tags` might be useful to build more complex configurations in Prometheus. As an example, an `alert` tag can be extracted to dine alerting routes based on the tag value.

**Example:**

Extract `group` and `alert` from a list of tags like this: `__meta_pve_tags="alert:team-1,group:cluster-1,node:node-1"`

```YAML
relabel_configs:
- source_labels:
  - __meta_pve_tags
  regex: ".*group:([\w\-_]*)"
  target_label: "group"
  replacement: "${1}"
- source_labels:
  - __meta_pve_tags
  regex: ".*alert:([\w\-_]*)"
  target_label: "alert"
  replacement: "${1}"
```

Use the extracted `alert` label to set an Alertmanager route:

```YAML
routes:
- receiver: "empty"
  matchers:
  - alert = muted
- receiver: "team-1"
  matchers:
  - alert = team-1
```
