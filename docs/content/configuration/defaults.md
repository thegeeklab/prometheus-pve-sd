---
title: Default settings
---

```Shell
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
output_file_mode: "0640"

loop_delay: 300
# Run pve sd in a loop and discover hosts every n seconds (as defined in loop_delay).
# Can be disabled to run disovery only once.
service: true

exclude_state: []
# needs to be a list of strings
exclude_vmid: []
include_vmid: []

# can be used to exclude vms by tags (proxmox 6+)
exclude_tags: []
include_tags: []

pve:
    server:
    user:
    password:
    auth_timeout: 5
    verify_ssl: true

# Example
# pve:
#     server: proxmox.example.com
#     user: root
#     password: secure
#     auth_timeout: 5
#     verify_ssl: true
```

If `include_tags` and `exclude_tags` are set at the same time, the `exclude_tags` option takes presedence.

If `include_tags` is set, and you VM don't have any tags set, they will not show up!
