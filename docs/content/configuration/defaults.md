---
title: Default settings
---

<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<!-- spellchecker-disable -->
{{< highlight YAML "linenos=table" >}}
---
logging:
    # supported log levels: debug|info|warning|error|critical
    level: warning
    # supported log formats: console|json|simple
    format: console

metrics:
    enabled: true
    address: "127.0.0.1"
    port: 8000

output_file:
loop_delay: 300
# Run pve sd in a loop and discover hosts every n seconds (as defined in loop_delay).
# Can be disabled to run disovery only once.
service: true

exclude_state: []
# needs to be a list of strings
exclude_vmid: []

pve:
    server:
    user:
    password
    auth_timeout: 5
    verify_ssl: true

# Example
# pve:
#     server: proxmox.example.com
#     user: root
#     password: secure
#     auth_timeout: 5
#     verify_ssl: true
{{< /highlight >}}
<!-- spellchecker-enable -->
<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->
