# Authoring canonical rules

**Русский** | [English](../../en/maintainers/rules-authoring.md)

Canonical rule — Markdown-файл с TOML frontmatter:

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

Severity: `required`, `user_decision`, `preferred`, `conditional`, `optional`.

Правила должны описывать инженерные свойства и invariants, а не случайные implementation choices. Архитектурные решения должны оставаться `user_decision`, если пользователь не зафиксировал их в project-specific инструкциях.

`always`, `must` и `never` используются только для действительно универсальных требований.
