from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://secureops:secureops@localhost:5435/secureops"
    redis_url: str = "redis://localhost:6382/0"
    correlation_window_minutes: int = 30
    auto_correlation_interval_seconds: int = 15

    # Auth: demo tokens, jwt (HS256), or oidc (JWKS validation).
    auth_mode: str = "demo"
    jwt_secret: str = "secureops-dev-secret-change-me"
    jwt_issuer: str = "secureops-local"
    jwt_audience: str = "secureops-api"
    jwt_algorithm: str = "HS256"
    oidc_jwks_url: str | None = None

    llm_provider: str = "openai"
    llm_model: str = "gpt-5.6-luna"
    llm_api_key: str | None = None
    llm_base_url: str = "https://api.openai.com/v1"
    llm_timeout_seconds: float = 30.0
    ai_job_timeout_seconds: int = 120

    # Real HTTP tool adapter for get_service_health. Empty => simulated response.
    service_health_base_url: str = "http://127.0.0.1:8200/internal/probes"
    service_health_timeout_seconds: float = 5.0

    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    rag_top_k: int = 4

    mlflow_tracking_uri: str = "http://localhost:5000"
    training_base_model: str = "distilbert-base-uncased"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
