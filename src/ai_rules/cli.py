from __future__ import annotations

import os
from pathlib import Path

import typer

from ai_rules import __version__
from ai_rules.bootstrap import bootstrap as bootstrap_global
from ai_rules.detection import render_detection_report
from ai_rules.doctor import doctor_project
from ai_rules.errors import AirulesError
from ai_rules.explain import explain_project
from ai_rules.project import find_project_root
from ai_rules.sync import add_selection, init_project, sync_project

app = typer.Typer(no_args_is_help=True, help="Manage reusable AI engineering rules.")


@app.callback()
def main() -> None:
    """Manage reusable AI engineering rules."""


def _run(action) -> None:
    try:
        result = action()
    except AirulesError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=1) from exc
    for write in result.writes:
        state = "change" if write.changed else "unchanged"
        typer.echo(f"{state}: {write.path}")


@app.command()
def version() -> None:
    typer.echo(f"airules {__version__}")


@app.command("init")
def init_command(
    profile: str | None = typer.Option(None, "--profile"),
    dry_run: bool = typer.Option(False, "--dry-run"),
) -> None:
    root = Path.cwd().resolve()
    _run(lambda: init_project(root, profile=profile, dry_run=dry_run))


@app.command()
def sync(dry_run: bool = typer.Option(False, "--dry-run")) -> None:
    root = find_project_root(Path.cwd())
    _run(lambda: sync_project(root, dry_run=dry_run))


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
def bootstrap(dry_run: bool = typer.Option(False, "--dry-run")) -> None:
    home = Path.home()
    codex_raw = os.environ.get("CODEX_HOME")
    codex_home = Path(codex_raw).expanduser() if codex_raw else None
    try:
        result = bootstrap_global(home, codex_home=codex_home, dry_run=dry_run)
    except AirulesError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=1) from exc
    for write in result.writes:
        state = "change" if write.changed else "unchanged"
        typer.echo(f"{state}: {write.path}")
    typer.echo(result.cursor_note)
