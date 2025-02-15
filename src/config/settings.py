from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://secureops:secureops@localhost:5435/secureops"
    correlation_window_minutes: int = 30
    auto_correlation_interval_seconds: int = 15
    llm_provider: str = "openai"
    llm_model: str = "gpt-5.6-luna"
    llm_api_key: str | None = None
    llm_base_url: str = "https://api.openai.com/v1"
    llm_timeout_seconds: float = 30.0

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
