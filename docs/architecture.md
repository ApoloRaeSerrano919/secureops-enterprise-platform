# Architecture

## Event ingestion

Sources POST normalized events. Raw payloads are kept for evidence review.

## Correlation

Open events are grouped by principal, IP, or service inside a time window. Risk uses severity, event type, and how varied the activity is.

## Incidents

An incident is the durable case object. Events stay immutable and link through `incident_events`.

## Investigator

`src/ai/investigator.py` calls the OpenAI Responses API via `src/ai/llm_client.py`. Flow:

1. Optional analyst prompt is checked by the prompt guard
2. Incident timeline is loaded as primary evidence
3. RAG retrieves approved security docs (enrichment only; failure does not block investigation)
4. Structured model output is schema-validated (`InvestigationResult`)
5. Summary is persisted and an audit row is written

Synchronous path: `POST /incidents/{id}/ai-investigation`. Async path: Redis/RQ via `POST /incidents/{id}/ai-investigation/async` and `GET /jobs/{job_id}`. The investigator has no credentials to run tools; recommendations are advisory only.

## Tool gateway

1. Allowlist
2. Role check
3. Risk class
4. Human approval when required
5. Adapter (`get_service_health` uses real HTTP when `SERVICE_HEALTH_BASE_URL` is set; others simulated)
6. Audit row

