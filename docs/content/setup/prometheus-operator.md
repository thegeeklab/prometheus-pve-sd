---
title: Using Prometheus Operator
---

{{< toc >}}

As an alternative to local files service discovery Prometheus also support discoveries form HTTP endpoints. In a Kubernetes setup, with the Prometheus operator, it makes more sense to use this [HTTP SD](https://prometheus.io/docs/prometheus/latest/configuration/configuration/#http_sd_config) instead of mounting the output file of the `prometheus-pve-sd` to the container.

The `prometheus-pve-sd` module doesn't have a dedicated HTTP endpoint, therefore you need to use a web server sidecar, that hosts the static file. The following deployment configuration can serve as a starting point for most setups, and just requires some minor adjustments, depending on your Kubernetes setup.

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
          value: /tmp/pve/proxmox.json
        # Add more configurations here, or use a configMap or secret to inject the remaining configs
        volumeMounts:
        - name: pve-sd-output
          mountPath: /tmp/pve/
      volumes:
        - name: pve-sd-output
          emptyDir: {}
status: {}
```

Additionally you will need a service, that exposes the HTTP endpoint within Kubernetes so Prometheus can scrape it.

Service configuration:

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

After configuring and starting the service, Prometheus need to be [configured](/usage/getting-started/#prometheus-configuration) to use the external service discovery.
