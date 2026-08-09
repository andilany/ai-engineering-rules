from ai_rules.project_instructions import (
    PROJECT_INCOMPLETE_MARKER,
    PROJECT_INSTRUCTIONS_TEMPLATE,
    PROJECT_ONBOARDING_PROMPT,
    is_project_incomplete,
)


def test_project_template_is_structured_and_incomplete() -> None:
    assert PROJECT_INSTRUCTIONS_TEMPLATE.startswith(PROJECT_INCOMPLETE_MARKER)
    for heading in (
        "## Project purpose",
        "## Architecture and boundaries",
        "## Development workflow",
        "## Testing and verification",
        "## Business constraints",
        "## Operational constraints",
        "## Changes requiring explicit approval",
    ):
        assert heading in PROJECT_INSTRUCTIONS_TEMPLATE


def test_project_incomplete_marker_is_the_status_contract() -> None:
    assert is_project_incomplete(None)
    assert is_project_incomplete(PROJECT_INSTRUCTIONS_TEMPLATE)
    assert not is_project_incomplete("# Project\n\nConfirmed project rules.\n")


def test_onboarding_prompt_requires_user_confirmation_and_no_invented_decisions() -> None:
    assert "Ask me focused questions" in PROJECT_ONBOARDING_PROMPT
    assert "Do not invent business requirements or architectural decisions" in PROJECT_ONBOARDING_PROMPT
    assert "after I confirm" in PROJECT_ONBOARDING_PROMPT
    assert "airules sync" in PROJECT_ONBOARDING_PROMPT
    assert "airules doctor" in PROJECT_ONBOARDING_PROMPT
