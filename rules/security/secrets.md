+++
id = "security.secrets"
title = "Secrets"
severity = "required"
scopes = ["security"]
+++
# Secrets

- Never commit, print, log, expose, or copy secrets, passwords, API keys, private keys, refresh tokens, or sensitive `.env` values.
- Use the project's configuration/secret-management abstraction and provide only safe example placeholders in documentation.
- Rotate or invalidate exposed credentials rather than merely deleting them from the latest source tree.
