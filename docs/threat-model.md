# Threat model

## Prompt injection

Analyst text tries to override investigator rules.

Controls: prompt screening; investigator is advisory only; auth lives outside the model.

## Tool misuse

A high-risk action is proposed.

Controls: allowlist; role policy; human approval; argument checks; idempotency.

