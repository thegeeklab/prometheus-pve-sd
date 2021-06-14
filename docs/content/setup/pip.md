---
title: Using pip
---

<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<!-- spellchecker-disable -->
{{< highlight Shell "linenos=table" >}}
# From PyPI as unprivileged user
$ pip install prometheus-pve-sd --user

# .. or as root
$ sudo pip install prometheus-pve-sd

# From Wheel file
$ pip install https://github.com/thegeeklab/prometheus-pve-sd/releases/download/v0.1.0/prometheus_pve_sd-0.1.0-py3-none-any.whl
{{< /highlight >}}
<!-- spellchecker-enable -->
<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->
