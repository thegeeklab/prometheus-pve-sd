---
title: Environment Variables
---

<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<!-- spellchecker-disable -->
{{< highlight Shell "linenos=table" >}}
PROMETHEUS_PVE_SD_CONFIG_FILE=
# supported log levels: debug|info|warning|error|critical
PROMETHEUS_PVE_SD_LOG_LEVEL=warning
# supported log formats: console|json|simple
PROMETHEUS_PVE_SD_LOG_FORMAT=console
PROMETHEUS_PVE_SD_OUTPUT_FILE=
PROMETHEUS_PVE_SD_LOOP_DELAY=300
# Run pve sd in a loop and discover hosts every n seconds (as defined in PROMETHEUS_PVE_SD_LOOP_DELAY).
# Can be disabled to run disovery only once.
PROMETHEUS_PVE_SD_SERVICE=true
PROMETHEUS_PVE_SD_EXCLUDE_STATE=
PROMETHEUS_PVE_SD_EXCLUDE_VMID=
PROMETHEUS_PVE_SD_PVE_SERVER=
PROMETHEUS_PVE_SD_PVE_USER=
PROMETHEUS_PVE_SD_PVE_PASSWORD=
PROMETHEUS_PVE_SD_PVE_AUTH_TIMEOUT=5
PROMETHEUS_PVE_SD_PVE_VERIFY_SSL=true
{{< /highlight >}}
<!-- spellchecker-enable -->
<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->
