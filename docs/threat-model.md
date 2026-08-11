# Threat model

## Prompt injection

Analyst text tries to override investigator rules.

Controls: prompt screening; investigator is advisory only; auth lives outside the model.

## Tool misuse

A high-risk action is proposed.

Controls: allowlist; role policy; human approval; argument checks; idempotency.

## Privilege escalation

An analyst calls responder/admin tools.

Control: policy in application code before any adapter runs.

## Duplicate containment

Client retries the same revocation.

Control: unique idempotency key on `tool_requests`.

