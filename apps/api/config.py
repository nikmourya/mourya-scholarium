"""
Mourya Scholarium — Application Configuration
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # App
    app_env: str = "development"
    app_secret_key: str = "change-me"
    app_debug: bool = True
    cors_origins: str = "http://localhost:3000"
    use_sqlite: bool = True  # Set to False when PostgreSQL is available

    # PostgreSQL
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "mourya_scholarium"
    postgres_user: str = "mourya"
    postgres_password: str = "changeme"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Qdrant
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333

    # Anthropic
    anthropic_api_key: str = ""
    anthropic_model_opus: str = "claude-sonnet-4-20250514"
    anthropic_model_sonnet: str = "claude-sonnet-4-20250514"
    anthropic_model_haiku: str = "claude-sonnet-4-20250514"

    # Scholarly APIs
    semantic_scholar_api_key: Optional[str] = None
    crossref_mailto: str = ""
    core_api_key: Optional[str] = None
    openalex_mailto: str = ""

    # JWT
    jwt_secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 1440

    @property
    def database_url(self) -> str:
        if self.use_sqlite:
            return "sqlite+aiosqlite:///./mourya_scholarium.db"
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def database_url_sync(self) -> str:
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
