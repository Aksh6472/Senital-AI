"""
Sentinel AI — Centralized Configuration.

Loads from environment variables / .env file using Pydantic Settings.
"""

from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application-wide settings, loaded from env vars / .env file."""

    # ── App ─────────────────────────────────────────────────────
    app_name: str = "Sentinel AI"
    app_version: str = "0.1.0"
    debug: bool = False
    cors_origins: List[str] = Field(default=["http://localhost:3000"])

    # ── Database ────────────────────────────────────────────────
    database_url: str = "postgresql+asyncpg://sentinel:sentinel@localhost:5432/sentinel_ai"

    # ── JWT ─────────────────────────────────────────────────────
    jwt_secret_key: str = "change-me-to-a-real-secret-at-least-32-chars"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    # ── SMTP (Email Notifications) ──────────────────────────────
    smtp_host: str = "smtp.example.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = "noreply@sentinel-ai.local"

    # ── Twilio (SMS/Voice Notifications) ────────────────────────
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_from_number: str = ""

    # ── S3-compatible Evidence Storage ──────────────────────────
    s3_endpoint_url: str = "http://localhost:9000"
    s3_access_key: str = "minioadmin"
    s3_secret_key: str = "minioadmin"
    s3_bucket_name: str = "sentinel-evidence"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


# Singleton — import this from anywhere
settings = Settings()
