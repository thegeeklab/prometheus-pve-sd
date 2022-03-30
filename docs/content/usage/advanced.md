---
title: Getting Started
---

{{< toc >}}

## Prometheus relabeling

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

Extract `group` and `alert` from a list of tags like this: `__meta_pve_tags="alert_team-1,group_cluster-1,node_node-1"`

```YAML

relabel_configs:
- source_labels:
  - __meta_pve_tags
  regex: ".*group_([\w\-_]*)"
  target_label: "group"
  replacement: "${1}"
- source_labels:
  - __meta_pve_tags
  regex: ".*alert_([\w\-_]*)"
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
