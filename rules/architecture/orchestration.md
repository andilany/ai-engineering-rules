+++
id = "architecture.orchestration"
title = "Orchestration"
severity = "user_decision"
scopes = ["architecture"]
+++
# Orchestration

- Choosing orchestration versus choreography is a user architecture decision.
- The agent may recommend orchestration when explicit workflow state, SLAs, retries, compensation, visibility, or human approval require central coordination, but must not migrate the project without approval.
