"""
Centralised configuration.

All secrets (DB password, JWT secret, API keys) are injected as CI/CD
variables (masked + protected) in GitLab and surfaced to the app as
environment variables at deploy time -- never committed to the repo.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    environment: str = "dev"
    database_url: str = "sqlite:///./local.db"
    jwt_secret: str = "changeme-local-only"
    api_key: str = ""
    celery_broker_url: str = "redis://localhost:6379/0"

    class Config:
        env_file = ".env"


settings = Settings()
