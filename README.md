# SecureOps Enterprise AI Platform — Resume-Matched Study Edition

SecureOps is an AI-assisted security operations backend built as a study project for senior backend, AI platform, MLOps and security engineering. It correlates security events into incidents, enriches investigations with RAG, asks a real LLM for structured evidence-grounded analysis, and keeps privileged actions behind deterministic RBAC/policy/human approval.

## Architecture

```text
TypeScript/Node event gateway
          |
          v
Python/FastAPI API ---> PostgreSQL + pgvector <--- Hugging Face embeddings / RAG
     |          |
     |          +--> Redis/RQ ---> async worker ---> real LLM
     |                                      |
     |                                      +--> MLflow eval tracking
     |
     +--> policy + RBAC + approval + idempotency ---> controlled tools
     |
     +--> Prometheus metrics / audit trail

ML workflows: PyTorch + Transformers + PEFT LoRA/optional QLoRA
Platform: Docker Compose, Kubernetes, Terraform/AWS, GitHub Actions, CloudWatch/IAM/Secrets Manager
MCP: read-only incident/knowledge tools + policy preview; privileged execution stays in SecureOps.
```

## Skills represented

See `docs/resume-skill-map.md`. The project includes Python, TypeScript, Node.js, FastAPI, PostgreSQL, Redis, AWS, Docker, Kubernetes, Terraform, GitHub Actions, CloudWatch, IAM, Secrets Manager, PyTorch, Hugging Face, RAG, MLflow, LLM security, MCP, LoRA and an optional QLoRA setup.

## Security model

The LLM is an investigator, not an authorization system. Incident logs and retrieved documents are untrusted data. Model output is schema validated. Recommendations never directly execute infrastructure changes. Mutating tool requests still pass through allowlists, RBAC, risk classification, approval, idempotency and audit logging.

## Local startup

```bash
cp .env.example .env
# add LLM_API_KEY to .env
docker compose up --build -d

docker compose exec api python scripts/init_db.py   # alembic upgrade head
docker compose exec api python scripts/seed_demo.py
# Optional RAG (needs requirements-rag / Dockerfile.rag + pgvector):
# docker compose exec api python scripts/index_knowledge.py
```

Correlation runs automatically via the `correlation-worker` service; you can still trigger it manually with `POST /correlate`.

Endpoints:

- API/Swagger: `http://localhost:8200/docs`
- Prometheus metrics: `http://localhost:8200/metrics`
- Node/TypeScript gateway: `http://localhost:8300`
- MLflow: `http://localhost:5000`

### Auth

Default `AUTH_MODE=demo` accepts study tokens `analyst-token`, `responder-token`, `admin-token`.

JWT study mode:

```bash
# .env: AUTH_MODE=jwt
python scripts/mint_dev_jwt.py --role analyst
# Authorization: Bearer <token>
```

OIDC sketch: set `AUTH_MODE=oidc`, `OIDC_JWKS_URL`, `JWT_ISSUER`, and `JWT_AUDIENCE` to validate IdP-signed tokens against JWKS.

### Dependencies / images

| File | Purpose |
|------|---------|
| `requirements-api.txt` / `Dockerfile` | Slim API + workers (no torch) |
| `requirements-rag.txt` / `Dockerfile.rag` | Optional RAG embeddings stack |
| `requirements-ml.txt` | LoRA/PEFT study extras |
| `requirements-ci.txt` | CI compileall/pytest/evals |

`get_service_health` performs a real outbound HTTP GET to `SERVICE_HEALTH_BASE_URL/{service}/health` (defaults to the API's `/internal/probes` route). Empty base URL falls back to simulated data.

## LLM + RAG investigation

`POST /incidents/{id}/ai-investigation` performs synchronous investigation. `POST /incidents/{id}/ai-investigation/async` queues the same work through Redis/RQ; inspect it with `GET /jobs/{job_id}`. RAG retrieves relevant approved security documentation through Hugging Face embeddings and pgvector, but retrieval is enrichment only: a RAG failure does not disable incident response.

## ML / MLOps exercises

Train the compact severity classifier:

```bash
python -m src.ml.train_classifier
```

Run a short LoRA fine-tune:

```bash
pip install -r requirements-ml.txt
python -m src.ml.train_lora --mode lora
```

QLoRA is provided as an optional NVIDIA/CUDA study path:

```bash
pip install -r requirements-ml-gpu.txt
python -m src.ml.train_lora --mode qlora
```

Without CUDA, QLoRA exits with a clear skip reason instead of training.
Track prompt-injection evaluation metrics in MLflow:

```bash
python -m src.evaluation.mlflow_eval
```

## MCP

Run the MCP server with:

```bash
python -m src.mcp_server.server
```

It exposes incident context, RAG knowledge search and policy evaluation. It intentionally does **not** expose direct privileged execution.

## Production gaps to discuss in interviews

This repository demonstrates architecture and controls; it is not a claim of a 1.5M-request production system. A production rollout should harden the JWT/OIDC sketch (token revocation, short TTL, proper secret management), managed RDS/ElastiCache, EKS deployment automation, TLS/ingress/WAF, secret rotation, OpenTelemetry traces, SLOs/alerts, model/version governance, data-retention controls, load testing, disaster recovery and deeper adversarial/evaluation datasets.
