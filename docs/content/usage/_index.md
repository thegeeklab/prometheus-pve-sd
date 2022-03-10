---
title: Usage
---

{{< toc >}}

## Start PVE SD

Create a [configuration file](/configuration/defaults/) with the required parameters to connect to your PVE server before you start the service.

```Shell
run prometheus-pve-sd -vv --loop-delay 900 -o /etc/prometheus/pve.json
```

## Available Labels

The following list of meta labels can be used to relabel your scrape results:

`__meta_pve_ipv4`

`__meta_pve_ipv6`

`__meta_pve_name`

`__meta_pve_type`

`__meta_pve_vmid`

`__meta_pve_cpu`

`__meta_pve_cores`

`__meta_pve_memory`

`__meta_pve_status`

`__meta_pve_tags`
: A comma-separated list of tags, as set on proxmox. Tags are supported by Proxmox 6+, and the field is missing if not tags are present on a VM

`__meta_pve_groups`
: Groups will be discovered from the `Notes` field of a host and need to be set as JSON e.g. `{"groups":["group1","group2"]}`

## Prometheus configuration

This example configuration snippet for the Prometheus `scrape_config` Prometheus to scrape `telegraf` assuming that it is deployed on all your servers.

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

### IPv4 or IPv6 usage
Set the address from the ipv4 or ipv6 meta label, and not the name
```YAML
relabel_configs:
- replacement: ${1}:9273
  source_labels:
  - __meta_pve_ipv4
  target_label: __address__
```

## Convert tags to custom labels
Eg. Extract `group` and `alert` from a list of tags like this: `__meta_pve_tags="alert:team-1,group:cluster-1,node:node-1"`
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

Using the `alert` label, you can then for example set an alertmanager route, for this alert
```YAML
routes:
- receiver: "empty"
  matchers:
  - alert = muted
- receiver: "team-1"
  matchers:
  - alert = team-1
```