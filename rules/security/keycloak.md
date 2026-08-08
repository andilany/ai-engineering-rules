+++
id = "security.keycloak"
title = "Keycloak"
severity = "preferred"
scopes = ["security"]
+++
# Keycloak

- For greenfield centralized identity in this profile, prefer Keycloak when it fits deployment and operations.
- Existing identity providers take precedence; migration to Keycloak requires explicit user approval.
- Keep realm/client configuration reproducible and avoid embedding administrative credentials in application code.
