+++
id = "backend.async-python"
title = "Async Python"
severity = "preferred"
scopes = ["python", "backend"]
+++
# Async Python

- Prefer async I/O end-to-end for network, database, messaging, and filesystem operations when libraries provide real async support.
- Never wrap blocking CPU work or sync-only libraries in fake async and assume the event loop is protected; isolate blocking work appropriately.
- Avoid blocking calls in ASGI request handlers and async consumers.
- Make cancellation, timeouts, graceful shutdown, and bounded concurrency explicit where relevant.
