from __future__ import annotations

import argparse
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEMVER_TAG = re.compile(r"^v(?P<version>0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")


def fail(message: str) -> None:
    print(f"release metadata error: {message}", file=sys.stderr)
    raise SystemExit(1)


def read_version() -> str:
    data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    project = data["project"]
    if project.get("license") != "MIT":
        fail("pyproject.toml must declare license = \"MIT\"")
    if project.get("description") != "Reusable engineering rules for AI coding agents":
        fail("project description does not match the public release metadata")
    return str(project["version"])


def validate(tag: str | None) -> str:
    version = read_version()
    expected_tag = f"v{version}"

    if tag is not None:
        match = SEMVER_TAG.fullmatch(tag)
        if match is None:
            fail(f"tag must use vMAJOR.MINOR.PATCH format, got {tag!r}")
        if tag != expected_tag:
            fail(f"tag {tag!r} does not match project version {version!r}")

    license_text = (ROOT / "LICENSE").read_text(encoding="utf-8")
    if not license_text.startswith("MIT License\n"):
        fail("LICENSE must contain the MIT License")

    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    if f"## [{version}]" not in changelog:
        fail(f"CHANGELOG.md has no [{version}] section")

    notes = ROOT / "docs" / "releases" / f"{expected_tag}.md"
    if not notes.is_file():
        fail(f"missing release notes: {notes.relative_to(ROOT)}")

    for path in (ROOT / "README.md", ROOT / "README_EN.md"):
        lowered = path.read_text(encoding="utf-8").lower()
        if "mit license" not in lowered:
            fail(f"{path.name} must document the MIT License")

    return expected_tag


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate release metadata before tagging/publishing"
    )
    parser.add_argument("--tag", help="Expected Git tag, for example v0.3.0")
    args = parser.parse_args()

    expected_tag = validate(args.tag)
    print(f"release metadata OK: {expected_tag}")


if __name__ == "__main__":
    main()
