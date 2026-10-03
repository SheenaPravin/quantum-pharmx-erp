"""Central application configuration (12-factor, AWS-ready)."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Quantum PharmX BI"
    version: str = "0.1.0"
    database_url: str = "sqlite:///./pharmx.db"
    redis_url: str = "redis://localhost:6379/0"
    jwt_secret: str = "dev-only-change-me"
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 480
    llm_provider: str = "gateway"  # abstraction — OpenAI/Azure/Open approved models via gateway
    llm_model: str = "pharmx-default"
    vector_backend: str = "pgvector"  # pgvector initially; qdrant/milvus at scale

    class Config:
        env_prefix = "PHARMX_"
        env_file = ".env"


settings = Settings()
