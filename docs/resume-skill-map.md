# Resume skill map

| Skill | Where it shows up |
|-------|-------------------|
| Python / FastAPI | [`apps/api/main.py`](../apps/api/main.py), [`src/`](../src/) |
| TypeScript / Node.js | [`services/event-gateway/`](../services/event-gateway/) |
| PostgreSQL + pgvector | [`src/db/`](../src/db/), [`src/rag/`](../src/rag/), Compose `db` |
| Redis / RQ | [`src/queueing/`](../src/queueing/), [`workers/rq_worker.py`](../workers/rq_worker.py) |
| Event correlation | [`src/incidents/correlation.py`](../src/incidents/correlation.py), [`workers/correlation_worker.py`](../workers/correlation_worker.py) |
| LLM investigation | [`src/ai/investigator.py`](../src/ai/investigator.py), [`src/ai/llm_client.py`](../src/ai/llm_client.py) |
| RAG / Hugging Face embeddings | [`src/rag/`](../src/rag/), [`scripts/index_knowledge.py`](../scripts/index_knowledge.py) |
| LLM security / prompt guard | [`src/security/prompt_guard.py`](../src/security/prompt_guard.py), [`evals/`](../evals/) |
| RBAC / policy / approval | [`src/auth/`](../src/auth/), [`src/tools/`](../src/tools/) |
| MCP | [`src/mcp_server/`](../src/mcp_server/) |
| PyTorch / Transformers | [`src/ml/train_classifier.py`](../src/ml/train_classifier.py) |
| LoRA / PEFT | [`src/ml/train_lora.py`](../src/ml/train_lora.py) |
| QLoRA (optional CUDA) | [`requirements-ml-gpu.txt`](../requirements-ml-gpu.txt), `train_lora --mode qlora` |
| MLflow | [`src/evaluation/mlflow_eval.py`](../src/evaluation/mlflow_eval.py), Compose `mlflow` |
| Docker Compose | [`docker-compose.yml`](../docker-compose.yml), [`Dockerfile`](../Dockerfile) |
| Kubernetes | [`infrastructure/kubernetes/`](../infrastructure/kubernetes/) |
| Terraform / AWS | [`infrastructure/terraform/`](../infrastructure/terraform/) (ECR, IAM, Secrets Manager, CloudWatch) |
| GitHub Actions | [`.github/workflows/ci.yml`](../.github/workflows/ci.yml) |
| Alembic migrations | [`alembic/`](../alembic/), [`scripts/init_db.py`](../scripts/init_db.py) |
| JWT / OIDC auth sketch | [`src/auth/service.py`](../src/auth/service.py), [`scripts/mint_dev_jwt.py`](../scripts/mint_dev_jwt.py) |
| HTTP tool adapter | [`src/tools/registry.py`](../src/tools/registry.py) `get_service_health` |
| Slim API image | [`Dockerfile`](../Dockerfile), [`requirements-api.txt`](../requirements-api.txt) |
| Prometheus metrics | [`src/observability/`](../src/observability/), `GET /metrics` |
