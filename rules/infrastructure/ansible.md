+++
id = "infrastructure.ansible"
title = "Ansible"
severity = "conditional"
scopes = ["infrastructure"]
+++
# Ansible

- Use Ansible for repeatable host configuration when the project already uses it or host provisioning warrants configuration management.
- Make roles idempotent, secrets external, and changes reviewable; do not mutate hosts without explicit user approval.
