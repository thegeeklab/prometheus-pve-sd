---
title: Using docker
---

```Shell
docker run \
    -e PROMETHEUS_PVE_SD_LOG_LEVEL=info \
    -e PROMETHEUS_PVE_SD_LOG_FORMAT=console \
    -e PROMETHEUS_PVE_SD_OUTPUT_FILE=/out/pve.json \
    -e PROMETHEUS_PVE_SD_SERVICE=false \
    -e PROMETHEUS_PVE_SD_PVE_SERVER=pve.example.com \
    -e PROMETHEUS_PVE_SD_PVE_USER=root \
    -e PROMETHEUS_PVE_SD_PVE_PASSWORD=secure \
    -e PY_COLORS=1 \
    -v $(pwd):/out \
    thegeeklab/prometheus-pve-sd
```

{{< hint type=note >}}
Keep in mind, that you have to pass SELinux labels (:Z or :z) to your mount option if you are working on SELinux enabled systems.
{{< /hint >}}

After configuring and starting the service, Prometheus need to be [configured](/usage/getting-started/#prometheus-configuration) to use the external service discovery.
