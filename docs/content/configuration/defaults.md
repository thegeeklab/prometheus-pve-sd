---
title: Default settings
---

```Shell
---
logging:
    # Supported log levels: debug|info|warning|error|critical
    level: warning
    # Supported log formats: console|json|simple
    format: console

metrics:
    enabled: true
    address: "127.0.0.1"
    port: 8000

output_file:
output_file_mode: "0640"

loop_delay: 300
# Run pve sd in a loop and discover hosts every n seconds (as defined in loop_delay).
# Can be disabled to run discovery only once.
service: true

exclude_state: []

# Needs to be a list of strings.
exclude_vmid: []
include_vmid: []

# Can be used to exclude vms by tags (proxmox 6+) - needs to be a list of strings.
# If `include_tags` and `exclude_tags` are set at the same time, the `exclude_tags` option takes precedence.
# If `include_tags` is set, and your VM don't have any tags set, they will not show up!
exclude_tags: []
include_tags: []

# Can be used to exclude discovered IP addresses that fall within the given networks
# (CIDR notation) - needs to be a list of strings. Loopback and link-local addresses are
# always excluded regardless of this setting. Useful for ignoring IPs handed out by
# Tailscale, Docker bridges or other virtual interfaces that Prometheus should not scrape.
# If an IP is excluded, discovery falls back to the next address found on the instance.
#
# Example:
# exclude_networks:
#     - 100.64.0.0/10   # Tailscale CGNAT range
#     - 172.17.0.0/16   # Default docker0 bridge
exclude_networks: []

# Set either password or token_name and token_value
pve:
    # May include an optional port (`hostname:port`).
    server:
    user:
    password:
    token_name:
    token_value:
    auth_timeout: 5
    verify_ssl: true

# Example with password
# pve:
#     server: proxmox.example.com
#     user: root
#     password: secure
#     auth_timeout: 5
#     verify_ssl: true

# Example with API token
# pve:
#     server: proxmox.example.com
#     user: root
#     token_name: pve_sd
#     token_value: 01234567-89ab-cdef-0123-456789abcdef
#     auth_timeout: 5
#     verify_ssl: true
```
