+++
id = "quality.ruff"
title = "Ruff"
severity = "required"
scopes = ["python", "quality"]
+++
# Ruff

- Python projects in this profile must use Ruff for linting/format consistency.
- Fix the underlying issue rather than disabling rules globally; targeted ignores require a concrete reason.
- Preserve an existing Ruff configuration unless a requested change requires updating it.
