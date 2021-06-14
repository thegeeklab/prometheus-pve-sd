---
title: Using docker
---

<!-- prettier-ignore-start -->
<!-- spellchecker-disable -->
{{< highlight Shell "linenos=table" >}}
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
{{< /highlight >}}
<!-- spellchecker-enable -->
<!-- prettier-ignore-end -->

{{< hint info >}}
**Info**\
Keep in mind, that you have to pass SELinux labels (:Z or :z) to your mount option if you are working on SELinux enabled systems.
{{< /hint >}}
