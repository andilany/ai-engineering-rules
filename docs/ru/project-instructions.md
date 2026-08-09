# Project-specific инструкции

**Русский** | [English](../en/project-instructions.md)

`.ai-rules/project.md` — user-owned слой правил конкретного репозитория. Он нужен для информации, которую нельзя надёжно выразить общими technology rules: назначение продукта, архитектурные границы, бизнес-ограничения, обязательные команды проверки и действия, требующие отдельного согласования.

`airules sync` и `airules reconfigure` не перезаписывают заполненный `project.md`.

## Onboarding status

Новый файл начинается с marker:

```html
<!-- airules:project-status=incomplete -->
```

Пока marker присутствует, `airules doctor` сообщает `project_rules_incomplete`. После завершения onboarding пользователь или его AI-agent удаляет marker.

## Как заполнять с помощью своего AI

После `airules init` CLI печатает готовый prompt. Его можно передать Cursor, Claude Code, Codex, Copilot или Gemini в открытом репозитории.

AI должен:

1. проанализировать структуру, конфигурацию, тесты и документацию;
2. выписать только факты, которые можно проверить в репозитории;
3. задать пользователю отдельные вопросы о назначении проекта, архитектурных решениях, бизнес- и operational-ограничениях;
4. не придумывать требования и решения;
5. показать предлагаемый текст до записи;
6. изменить только `.ai-rules/project.md` после подтверждения пользователя;
7. удалить incomplete marker только после согласования содержимого.

## Рекомендуемые разделы

- Project purpose
- Architecture and boundaries
- Development workflow
- Testing and verification
- Business constraints
- Operational constraints
- Changes requiring explicit approval

После редактирования выполните:

```bash
airules sync
airules doctor
```

Это обновит native projections для тех adapters, которые включают project-specific инструкции.

## Удаление

Обычный `airules uninstall` сохраняет `.ai-rules/project.md`. Полное удаление выполняется только явно:

```bash
airules uninstall --purge
```
