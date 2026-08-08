# Native Agent Adapters for airules 0.3.0

## Goal

Replace thin shared-file adapters with native instruction formats for Cursor, Claude Code, and GitHub Copilot while keeping Codex intentionally small and retaining the IDE-independent compiled snapshot.

## Canonical source and shared project files

`rules/**/*.md` remains the canonical rule catalog. Profiles, detection, manifest flags, explicit includes/excludes, and precedence compose an `EffectiveRules` graph.

Every initialized project keeps:

- `.ai-rules/generated.md` — complete generated snapshot of the effective rule set for auditing, `explain`, debugging, Gemini, and Codex navigation.
- `.ai-rules/project.md` — user-owned project-specific instructions, never overwritten by sync.

Native adapters must be projections of the same `EffectiveRules`; they must not define a second source of truth.

## Supported agents

`--ide` supports exactly:

- `codex`
- `claude`
- `cursor`
- `copilot`
- `gemini`

Legacy manifests without `ides` mean all supported agents, including Copilot after upgrading to 0.3.0.

## Native grouping model

Effective canonical rules are grouped by the first scope/domain implied by their rule id into stable ordered buckets:

1. `000-core` — `core.*`
2. `100-architecture` — `architecture.*`
3. `200-security-quality` — `security.*`, `quality.*`
4. `300-language-backend` — `languages.*`, `backend.*`
5. `400-data-messaging` — `data.*`, `messaging.*`
6. `500-frontend` — `frontend.*`
7. `600-ml-infrastructure` — `ml.*`, `infrastructure.*`

Empty groups are not emitted. Within each group preserve the global severity order and effective rule order. Render source/rule provenance comments where the target format permits HTML comments.

## Cursor adapter

Generate only airules-owned project rules under `.cursor/rules/`:

- `airules-000-core.mdc`
- `airules-100-architecture.mdc`
- `airules-200-security-quality.mdc`
- `airules-300-language-backend.mdc`
- `airules-400-data-messaging.mdc`
- `airules-500-frontend.mdc`
- `airules-600-ml-infrastructure.mdc`
- `airules-999-project.mdc`

Canonical generated group files contain their instructions directly and use MDC frontmatter with `alwaysApply: true`. Version 0.3.0 deliberately does not infer file globs from semantic scopes.

`airules-999-project.mdc` is an always-on bridge to the user-owned `.ai-rules/project.md`. It may reference the project file using a repository-root relative Cursor `@` reference; generated canonical group files must not use `../../` references.

The old `.cursor/rules/engineering.mdc` is removed only when it contains the airules ownership marker. A user-owned file without the marker is never deleted or overwritten.

Stale `airules-*.mdc` files are deleted only when they contain the airules ownership marker and are no longer expected.

## Claude Code adapter

Generate native modular project rules under:

`.claude/rules/airules/*.md`

using the same group names (`000-core.md` ... `600-ml-infrastructure.md`). Claude discovers these recursively.

Keep root `CLAUDE.md` as a short managed entrypoint. It imports only `.ai-rules/project.md`; canonical generated rules are supplied natively through `.claude/rules/airules/` and must not be imported again from `generated.md`.

Airules-owned Claude modular files include an ownership marker. Stale owned files are removed safely; unrelated `.claude/rules` files are never touched.

No automatic `paths:` frontmatter is emitted in 0.3.0 because canonical semantic scopes are not precise filesystem globs.

## Codex adapter

Keep a short root `AGENTS.md` managed block. Codex natively reads `AGENTS.md` and more-specific nested instruction files, with more-specific instructions later in the chain.

The managed block instructs Codex to read `.ai-rules/generated.md` and `.ai-rules/project.md` before modifying the repository and states precedence. Do not generate nested `AGENTS.md` or `AGENTS.override.md`; those remain project/user-controlled.

The managed block should remain compact to avoid consuming unnecessary Codex instruction budget.

## GitHub Copilot adapter

Generate `.github/copilot-instructions.md` as a short repository-wide managed entrypoint. It imports or directs Copilot CLI to the user-owned `.ai-rules/project.md` and states that modular airules instructions live under `.github/instructions/airules/`.

Generate native modular files under:

`.github/instructions/airules/*.instructions.md`

using the same thematic groups. Each file uses frontmatter:

```yaml
---
applyTo: "**"
---
```

for 0.3.0 so all canonical engineering rules remain consistently available across supported Copilot environments. Path-specific narrowing is deferred until airules has explicit filesystem-scope metadata rather than semantic scopes.

The `.github/copilot-instructions.md` file is managed by a marker block so existing user content is preserved. Airules modular files are fully owned and use an ownership marker. Stale owned files are removed; unrelated `.github/instructions` files are untouched.

Copilot must not depend on incidental `AGENTS.md` or `CLAUDE.md` support because GitHub does not define a general precedence across multiple instruction types.

## Gemini adapter

Keep the existing thin `GEMINI.md` adapter in 0.3.0. It imports `.ai-rules/generated.md` and `.ai-rules/project.md`. Native Gemini modularization is outside this change unless official stable project-rule semantics justify it later.

## Bootstrap

- Codex: keep `$CODEX_HOME/AGENTS.md` / `~/.codex/AGENTS.md` universal-core managed block.
- Claude: move universal global generated rules to `~/.claude/rules/airules/` where possible; retain a compatibility path only when needed by tests/documentation.
- Cursor: continue writing `~/.ai-rules/cursor-user-rules.txt` for manual paste into Cursor User Rules because User Rules are settings-based plain text.
- Copilot: write user-level `$COPILOT_HOME/copilot-instructions.md` or `~/.copilot/copilot-instructions.md` for universal core; do not mutate application settings.
- Gemini: preserve current global behavior.

Bootstrap selection obeys repeated `--ide` exactly as project init does.

## Ownership and safe deletion

Introduce explicit planned deletion support rather than deleting files ad hoc. Deletion is allowed only inside known adapter-owned prefixes and only for files whose contents prove airules ownership.

Sync must never delete arbitrary project files, user-owned adapter files, `.ai-rules/project.md`, or non-airules native rules.

Dry-run reports planned writes and deletions without changing disk state.

## Doctor

Doctor resolves `manifest.ides` exactly like sync and checks only selected agents.

For native adapters it verifies:

- expected native files exist and match rendered content;
- expected root entrypoint files match their managed content;
- stale airules-owned native files are reported;
- conflicting/unowned legacy files are reported without deletion;
- unselected agents are ignored.

## Testing and release validation

Follow TDD. Add RED tests before production changes.

Required coverage:

- group partitioning and stable ordering;
- Cursor native files, no `../../` canonical imports, legacy owned migration, stale cleanup, user-file preservation;
- Claude modular native files and short `CLAUDE.md` entrypoint;
- Copilot repository-wide + modular instructions, ownership and preservation;
- Codex compact entrypoint unchanged in architecture;
- `--ide copilot` validation/persistence;
- doctor behavior for every selected agent;
- dry-run and safe deletion behavior;
- legacy manifests;
- full installed-package smoke from an isolated package layout for `cursor`, `claude`, `codex`, and `copilot`.

Release version: `0.3.0`.
