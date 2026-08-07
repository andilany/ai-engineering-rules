+++
id = "core.external-actions"
title = "External Actions and Git"
severity = "required"
scopes = ["all"]
+++
# External Actions and Git

- Read-only Git inspection is allowed unless the user forbids it.
- Never create or switch branches, stage files, commit, push, merge, rebase, create pull requests, create repositories, create tags/releases, rewrite history, reset, clean, deploy, or mutate infrastructure without explicit user approval for that action.
- The user owns commits. Authorization to edit files does not authorize commit or push.
- Never perform an irreversible migration merely because a preferred rule recommends a different tool or architecture.
