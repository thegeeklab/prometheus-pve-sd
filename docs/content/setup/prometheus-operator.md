---
title: Use with prometheus operator
---

{{< toc >}}

## Use in Kubernetes with Prometheus operator

Prometheus also allows service discovery through a http endpoint, and not just through a file.
In a Kubernetes setup, with the prometheus operator, it makes more sense to use this [HTTP SD](https://prometheus.io/docs/prometheus/latest/configuration/configuration/#http_sd_config)
instead of trying to mount the output of the prometheus-pve-sd to the container.

Since the prometheus-pve-sd module doesn't have a dedicated http endpoint, you need to use a webserver sidecar, that
hosts the file as a static file.

The following deployment configuration can serve as a starting point for most setups, and will need some minor adjustments,
depending on your Kubernetes setup.

## Kubernetes configuration

Deployment configuration:

```YAML
apiVersion: apps/v1
kind: Deployment
metadata:
  creationTimestamp: null
  labels:
    app: proxmox-service-discovery
  name: proxmox-service-discovery
spec:
  replicas: 1
  selector:
    matchLabels:
      app: proxmox-service-discovery
  strategy: {}
  template:
    metadata:
      creationTimestamp: null
      labels:
        app: proxmox-service-discovery
    spec:
      containers:
      - image: nginx
        name: webserver
        resources: {}
        ports:
        - containerPort: 80
          protocol: TCP
          name: http
        volumeMounts:
        - name: pve-sd-output
          mountPath: /usr/share/nginx/html
      - image: thegeeklab/prometheus-pve-sd
        name: prometheus-pve-sd
        resources: {}
        env:
        - name: PROMETHEUS_PVE_SD_OUTPUT_FILE
          value: /tmp/pve/pve-sd.json
        # Add more configurations here, or use a configMap or secret to inject the remaining configs
        volumeMounts:
        - name: pve-sd-output
          mountPath: /tmp/pve/
      volumes:
        - name: pve-sd-output
          emptyDir: {}
status: {}
```

Additionally you will need a service, that exposes the http endpoint within Kubernetes so prometheus can scrape it.

service configuration

```YAML
apiVersion: v1
kind: Service
metadata:
  name: pve-sd-service
spec:
  selector:
    app: proxmox-service-discovery
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80
```

## Prometheus configuration

Prometheus needs to know which endpoint to check for target discovery, this is done similarly to a `file_sd_config`  
The following example assumes, that the above deployment is in the same namespace as the prometheus instance.

```YAML
- http_sd_configs:
    url: pve-sd-service:80/pve-sd.json
  job_name: pve-service-discovery
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

See [useage](/usage/) for more details on the relabel configuration
