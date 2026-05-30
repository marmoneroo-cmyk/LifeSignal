"""Application configuration loaded from the environment."""
from __future__ import annotations

import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

DISCLAIMER = (
    "This system does not provide a medical diagnosis and should not replace "
    "consultation with qualified healthcare professionals."
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Empty -> fall back to a local SQLite file so the app runs with zero setup.
    database_url: str = ""
    cors_origins: str = "http://localhost:3000"

    # Optional: enables Claude-powered report narration. Without it, the app
    # falls back to a deterministic rule-based summary (no key required).
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-6"

    # Secret for signing local JWTs. OVERRIDE in production via env (JWT_SECRET).
    jwt_secret: str = "dev-only-insecure-secret-change-me"

    @property
    def sqlalchemy_url(self) -> str:
        if self.database_url:
            return self.database_url
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "health_intel.db")
        return f"sqlite:///{db_path}"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
