# Architecture

## Event ingestion

Sources POST normalized events. Raw payloads are kept for evidence review.

## Correlation

Open events are grouped by principal, IP, or service inside a time window. Risk uses severity, event type, and how varied the activity is.

## Incidents

An incident is the durable case object. Events stay immutable and link through `incident_events`.

## Investigator

`src/ai/investigator.py` calls the OpenAI Responses API through `src/ai/llm_client.py`, validates structured output (summary, observations, hypotheses, cited event IDs, recommended actions), and stores the result on the incident. Recommendations are advisory only; the investigator has no credentials to run tools.

