# Architecture

## Event ingestion

Sources POST normalized events. Raw payloads are kept for evidence review.

## Correlation

Open events are grouped by principal, IP, or service inside a time window. Risk uses severity, event type, and how varied the activity is.

## Incidents

An incident is the durable case object. Events stay immutable and link through `incident_events`.

