from __future__ import annotations

import os
import sys
from pathlib import Path

import typer

from ai_rules import __version__
from ai_rules.bootstrap import bootstrap as bootstrap_global
from ai_rules.detection import detect_project, render_detection_report
from ai_rules.doctor import doctor_project
from ai_rules.errors import AirulesError, ConfigurationError
from ai_rules.explain import explain_project
from ai_rules.lifecycle import configure_project, detected_manifest, uninstall_project
from ai_rules.project import ProjectPaths, find_project_root
from ai_rules.project_instructions import PROJECT_ONBOARDING_PROMPT
from ai_rules.sync import add_selection, init_project, sync_project
from ai_rules.wizard import render_selection_summary, run_wizard

app = typer.Typer(no_args_is_help=True, help="Manage reusable AI engineering rules.")


@app.callback()
def main() -> None:
    """Manage reusable AI engineering rules."""


def _print_result(result) -> None:
    for write in result.writes:
        state = "change" if write.changed else "unchanged"
        typer.echo(f"{state}: {write.path}")
    for delete in getattr(result, "deletes", ()):
        state = "delete" if delete.changed else "unchanged-delete"
        typer.echo(f"{state}: {delete.path}")
    for warning in getattr(result, "warnings", ()):
        typer.echo(f"WARN: {warning}", err=True)


def _run(action) -> None:
    try:
        result = action()
    except AirulesError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=1) from exc
    _print_result(result)


def _print_preview(result) -> bool:
    changed = False
    for write in result.writes:
        if not write.changed:
            continue
        changed = True
        action = "MODIFY" if write.path.exists() else "CREATE"
        typer.echo(f"  {action:<6} {write.path}")
    for delete in getattr(result, "deletes", ()):
        if not delete.changed:
            continue
        changed = True
        typer.echo(f"  DELETE {delete.path}")
    for warning in getattr(result, "warnings", ()):
        typer.echo(f"  WARN  {warning}", err=True)
    return changed


def _confirm(message: str, *, yes: bool) -> bool:
    if yes:
        return True
    if typer.confirm(message, default=False):
        return True
    typer.echo("Cancelled. No changes were made.")
    return False


def _interactive_terminal() -> bool:
    return sys.stdin.isatty() and sys.stdout.isatty()


def _use_interactive_init(
    *,
    profile: str | None,
    ide: list[str] | None,
    interactive: bool | None,
) -> bool:
    if interactive is not None:
        return interactive
    if profile is not None or ide:
        return False
    return _interactive_terminal()


def _print_project_onboarding() -> None:
    typer.echo("\nProject-specific instructions still need your input.")
    typer.echo(
        "Open your preferred AI coding agent in this repository and give it the prompt below. "
        "The agent should inspect the project, ask you questions, and only write confirmed facts."
    )
    typer.echo("\nSuggested prompt:\n")
    typer.echo(PROJECT_ONBOARDING_PROMPT, nl=False)


@app.command()
def version() -> None:
    typer.echo(f"airules {__version__}")


@app.command("init")
def init_command(
    profile: str | None = typer.Option(None, "--profile"),
    ide: list[str] | None = typer.Option(
        None, "--ide", help="IDE/agent adapter to manage; repeatable."
    ),
    interactive: bool | None = typer.Option(
        None,
        "--interactive/--no-interactive",
        help="Force or disable the interactive project setup wizard.",
    ),
    yes: bool = typer.Option(False, "--yes", "-y", help="Accept the final wizard summary."),
    dry_run: bool = typer.Option(False, "--dry-run"),
) -> None:
    root = Path.cwd().resolve()
    paths = ProjectPaths(root)
    selected_ides = tuple(ide) if ide else None
    had_project_rules = paths.project_rules.exists()

    if not _use_interactive_init(profile=profile, ide=ide, interactive=interactive):
        _run(
            lambda: init_project(
                root,
                profile=profile,
                dry_run=dry_run,
                ides=selected_ides,
            )
        )
        if not dry_run and not had_project_rules and paths.project_rules.exists():
            _print_project_onboarding()
        return
    if paths.manifest.exists():
        typer.echo("Error: Project is already initialized; run `airules reconfigure`.", err=True)
        raise typer.Exit(code=1)
    detections = detect_project(root)
    typer.echo(render_detection_report(root), nl=False)
    try:
        manifest, selection = run_wizard(detections, rules_version=__version__)
    except (EOFError, KeyboardInterrupt) as exc:
        typer.echo("Cancelled. No changes were made.")
        raise typer.Exit() from exc
    typer.echo("\n" + render_selection_summary(selection), nl=False)
    if not dry_run and not _confirm("Apply this configuration?", yes=yes):
        return
    _run(lambda: configure_project(root, manifest, dry_run=dry_run, replace_existing=False))
    if not dry_run and not had_project_rules and paths.project_rules.exists():
        _print_project_onboarding()


@app.command()
def reconfigure(
    profile: str | None = typer.Option(None, "--profile"),
    ide: list[str] | None = typer.Option(
        None, "--ide", help="IDE/agent adapter to manage; repeatable."
    ),
    interactive: bool | None = typer.Option(
        None,
        "--interactive/--no-interactive",
        help="Force or disable the interactive project setup wizard.",
    ),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompts."),
    dry_run: bool = typer.Option(False, "--dry-run"),
) -> None:
    root = find_project_root(Path.cwd())
    paths = ProjectPaths(root)
    if not paths.manifest.exists():
        typer.echo("Error: Project is not initialized; run `airules init`.", err=True)
        raise typer.Exit(code=1)
    had_project_rules = paths.project_rules.exists()
    preview = uninstall_project(root, purge=False, dry_run=True)
    typer.echo("⚠ Current airules configuration will be replaced.")
    typer.echo("The following managed data will be removed or rewritten:")
    _print_preview(preview)
    if paths.project_rules.exists():
        typer.echo(f"  KEEP   {paths.project_rules} (user-owned project instructions)")
    typer.echo("No files are changed until the new wizard configuration is confirmed.")
    if not dry_run and not _confirm("Continue and reset the current configuration?", yes=yes):
        return
    selected_ides = tuple(ide) if ide else None
    use_interactive = interactive if interactive is not None else not (profile is not None or ide)
    if use_interactive:
        detections = detect_project(root)
        typer.echo("\n" + render_detection_report(root), nl=False)
        try:
            manifest, selection = run_wizard(detections, rules_version=__version__)
        except (EOFError, KeyboardInterrupt) as exc:
            typer.echo("Cancelled. No changes were made.")
            raise typer.Exit() from exc
        typer.echo("\n" + render_selection_summary(selection), nl=False)
        if not dry_run and not _confirm("Apply the new configuration?", yes=yes):
            return
    else:
        try:
            manifest = detected_manifest(root, profile=profile, ides=selected_ides)
        except AirulesError as exc:
            typer.echo(f"Error: {exc}", err=True)
            raise typer.Exit(code=1) from exc
    _run(lambda: configure_project(root, manifest, dry_run=dry_run, replace_existing=True))
    if not dry_run and not had_project_rules and paths.project_rules.exists():
        _print_project_onboarding()


@app.command()
def uninstall(
    purge: bool = typer.Option(
        False,
        "--purge",
        help="Also delete the user-owned .ai-rules/project.md file.",
    ),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip the confirmation prompt."),
    dry_run: bool = typer.Option(False, "--dry-run"),
) -> None:
    root = find_project_root(Path.cwd())
    paths = ProjectPaths(root)
    preview = uninstall_project(root, purge=purge, dry_run=True)
    typer.echo("⚠ airules will be removed from this project.")
    typer.echo("The following managed data will be deleted or modified:")
    changed = _print_preview(preview)
    if not purge and paths.project_rules.exists():
        typer.echo(f"  KEEP   {paths.project_rules} (use --purge to delete it)")
    if not changed:
        typer.echo("No airules-managed project data was found.")
        return
    if dry_run:
        typer.echo("Dry run only. No changes were made.")
        return
    if not _confirm("Continue with uninstall?", yes=yes):
        return
    _run(lambda: uninstall_project(root, purge=purge, dry_run=False))


@app.command()
def sync(
    ide: list[str] | None = typer.Option(
        None, "--ide", help="Temporary IDE/agent adapter override; repeatable."
    ),
    dry_run: bool = typer.Option(False, "--dry-run"),
) -> None:
    root = find_project_root(Path.cwd())
    selected_ides = tuple(ide) if ide else None
    _run(lambda: sync_project(root, dry_run=dry_run, ides=selected_ides))


@app.command("add")
def add_command(
    selection: str,
    dry_run: bool = typer.Option(False, "--dry-run"),
) -> None:
    root = find_project_root(Path.cwd())
    _run(lambda: add_selection(root, selection=selection, dry_run=dry_run))


@app.command()
def detect() -> None:
    root = find_project_root(Path.cwd())
    typer.echo(render_detection_report(root), nl=False)


@app.command()
def explain() -> None:
    root = find_project_root(Path.cwd())
    try:
        typer.echo(explain_project(root), nl=False)
    except AirulesError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=1) from exc


@app.command()
def doctor() -> None:
    root = find_project_root(Path.cwd())
    findings = doctor_project(root)
    for finding in findings:
        typer.echo(f"{finding.level} {finding.code}: {finding.message}")
    if any(finding.level == "ERROR" for finding in findings):
        raise typer.Exit(code=1)


@app.command()
def bootstrap(
    ide: list[str] | None = typer.Option(
        None, "--ide", help="IDE/agent bootstrap target; repeatable."
    ),
    dry_run: bool = typer.Option(False, "--dry-run"),
) -> None:
    home = Path.home()
    codex_raw = os.environ.get("CODEX_HOME")
    codex_home = Path(codex_raw).expanduser() if codex_raw else None
    copilot_raw = os.environ.get("COPILOT_HOME")
    copilot_home = Path(copilot_raw).expanduser() if copilot_raw else None
    selected_ides = tuple(ide) if ide else None
    try:
        result = bootstrap_global(
            home,
            codex_home=codex_home,
            copilot_home=copilot_home,
            dry_run=dry_run,
            ides=selected_ides,
        )
    except AirulesError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=1) from exc
    _print_result(result)
