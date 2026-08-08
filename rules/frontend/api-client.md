+++
id = "frontend.api-client"
title = "Frontend API Client"
severity = "conditional"
scopes = ["frontend"]
+++
# REST / WebSocket Client

- Use the project's existing Axios or Fetch convention; do not introduce both without need.
- Use REST for request/response APIs and WebSocket only when product requirements need live bidirectional/realtime updates.
- Centralize auth/error/retry behavior carefully and avoid infinite refresh/retry loops.
