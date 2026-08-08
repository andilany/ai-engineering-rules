# Authoring canonical rules

Каждое canonical rule — Markdown с TOML frontmatter:

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

## Severity

- `required` — invariant: безопасность, scope, honesty, required quality properties.
- `user_decision` — агент анализирует и рекомендует, но не принимает решение самостоятельно.
- `preferred` — default для greenfield, если проект/пользователь не выбрал другое.
- `conditional` — только когда технология или ситуация уже применима.
- `optional` — вариант, который можно предложить.

## Правила хорошего rule

Фиксируйте свойства и invariants, а не случайные implementation choices. Лучше «concurrent job claim must be atomic», чем «always use exactly one worker». Лучше «payment webhooks must be idempotent», чем «every project must use provider X».

`always`, `must` и `never` должны использоваться только для действительно универсальных invariants. Архитектурные решения (`microservices`, Kafka, orchestration/choreography, Kubernetes/GitOps) должны оставаться `user_decision`, если пользователь не зафиксировал их project-specific правилом.
