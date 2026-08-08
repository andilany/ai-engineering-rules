+++
id = "languages.python"
title = "Python"
severity = "preferred"
scopes = ["python"]
+++
# Python

- For greenfield work, prefer the latest stable Python release supported by the selected stable dependencies; avoid prerelease interpreter or dependency versions by default.
- For greenfield dependency management, prefer `uv`.
- Preserve an existing project's Python version and package manager unless the user approves a migration.
- You may recommend migration from Poetry, pip, or pip-tools to `uv` with concrete benefits, migration cost, and compatibility risks, but never apply that migration without explicit user approval.
- Use modern type syntax and explicit typing; avoid `Any` unless necessary and documented.
