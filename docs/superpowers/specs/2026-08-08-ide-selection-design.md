# IDE Selection for airules

## Goal

Allow users to select which supported agent/IDE adapters `airules` manages for a project or global bootstrap, without creating unrelated adapter files and without deleting files that already exist.

## Supported values

`codex`, `claude`, `cursor`, `gemini`.

The CLI accepts `--ide` repeatedly. Values are normalized to lowercase and validated against the supported set. Unknown values fail with a clear configuration error before any write is applied.

## Project manifest

`ProjectManifest` gains a persistent `ides: list[str]` field. `.ai-rules.toml` stores it as a top-level array:

```toml
ides = ["codex", "cursor"]
```

For backward compatibility, a manifest without `ides` means all supported IDEs. Existing projects therefore keep current behavior after upgrading.

`airules init --ide ...` stores the selected IDEs in the new manifest. If `--ide` is omitted, the manifest records all supported IDEs so the selection is explicit for newly initialized projects.

## Adapter generation

The generated rules snapshot `.ai-rules/generated.md` and the user-owned `.ai-rules/project.md` remain shared project files and are created independently of IDE selection.

Adapter files are mapped as follows:

- `codex` → `AGENTS.md`
- `claude` → `CLAUDE.md`
- `gemini` → `GEMINI.md`
- `cursor` → `.cursor/rules/engineering.mdc`

`init` renders only adapters selected by `manifest.ides`.

Normal `sync` reads `manifest.ides` and renders only those adapters.

`sync --ide ...` is a temporary adapter override for that invocation only. It does not modify `manifest.ides`. Shared generated rules are still refreshed normally.

A reduced selection never deletes, truncates, or rewrites an unselected adapter file. This is intentional: adapter ownership can overlap with user-authored content and deletion is destructive.

## Bootstrap

`airules bootstrap --ide ...` writes the Universal Core only for selected IDEs.

Without `--ide`, bootstrap preserves current behavior and prepares all supported targets.

Cursor remains special: `bootstrap --ide cursor` writes only `~/.ai-rules/cursor-user-rules.txt` plus the explanatory Cursor note. It does not modify Cursor Settings automatically.

When Cursor is not selected, no Cursor note is printed.

## CLI examples

```text
airules init --ide codex
airules init --ide codex --ide cursor
airules sync
airules sync --ide claude
airules bootstrap --ide codex
airules bootstrap --ide claude --ide gemini
```

`--ide` may appear multiple times and preserves the user's order after de-duplication.

## Error handling

- Unknown IDE: fail before writes with the supported values in the message.
- Empty selection is not representable through the CLI; omitting the option means the command default described above.
- Duplicate `--ide` values are de-duplicated.
- Existing manifest with an empty explicit `ides = []` is invalid and produces a configuration error rather than silently generating all adapters.

## Testing

TDD coverage must include:

1. manifest round-trip for `ides` and backward compatibility when absent;
2. `init --ide codex` creates Codex plus shared files, not Claude/Gemini/Cursor;
3. repeated `--ide` creates exactly the selected adapters;
4. normal `sync` respects persisted selection;
5. `sync --ide claude` temporarily writes Claude without changing manifest selection;
6. sync with a reduced selection does not delete pre-existing unselected adapter files;
7. bootstrap filters global writes and Cursor note correctly;
8. invalid IDE produces no project/global writes;
9. existing no-`ides` manifests still sync all adapters;
10. full existing test suite remains green.

## Non-goals

This change does not add `airules ide set/add/remove`, auto-detect the installed IDE, delete stale adapter files, migrate project architecture, or alter rule/profile composition.
