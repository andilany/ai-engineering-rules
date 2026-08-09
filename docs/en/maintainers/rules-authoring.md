# Authoring canonical rules

[Русский](../../ru/maintainers/rules-authoring.md) | **English**

A canonical rule is a Markdown file with TOML frontmatter:

```markdown
+++
id = "category.name"
title = "Human Title"
severity = "preferred"
scopes = ["python", "backend"]
+++
# Human Title

- Concrete guidance.
```

Severity levels are `required`, `user_decision`, `preferred`, `conditional`, and `optional`.

Rules should describe engineering properties and invariants rather than incidental implementation choices. Architecture choices should remain `user_decision` unless the user has fixed them in project-specific instructions.

Use `always`, `must`, and `never` only for genuinely universal requirements.
