# Architecture

## Event ingestion

Sources POST normalized events. Raw payloads are kept for evidence review.

## Correlation

Open events are grouped by principal, IP, or service inside a time window. Risk uses severity, event type, and how varied the activity is.

## Incidents

An incident is the durable case object. Events stay immutable and link through `incident_events`.

## Tool gateway

1. Allowlist
2. Role check
3. Risk class
4. Human approval when required
5. Adapter (simulated)
6. Audit row

## Idempotency

Tool requests carry an idempotency key so retries do not double-run containment.

## Approval

High-risk actions (e.g. `revoke_session`) stay `PENDING_APPROVAL` until a responder or admin approves.
