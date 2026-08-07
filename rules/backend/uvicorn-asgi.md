+++
id = "backend.uvicorn-asgi"
title = "Uvicorn and ASGI"
severity = "conditional"
scopes = ["python", "backend"]
+++
# Uvicorn and ASGI

- For greenfield FastAPI services, Uvicorn/ASGI is the preferred runtime baseline.
- Preserve an existing ASGI server or deployment runtime unless there is a concrete reason and user approval to change it.
- Configure proxy headers, timeouts, workers, graceful shutdown, and health checks according to the actual deployment model.
