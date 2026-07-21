import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv


load_dotenv()
DEV_SECRET = "change-this-development-secret-32-bytes-minimum"
_default_dev_origins = "http://127.0.0.1:8000,http://localhost:8000,http://127.0.0.1:5500,http://localhost:5500,null"
_environment = os.getenv("ENVIRONMENT", "development")


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "SentinelOps Cybersecurity Incident Platform")
    environment: str = _environment
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./cybersec_incidents.db")
    secret_key: str = os.getenv("SECRET_KEY", DEV_SECRET)
    access_token_minutes: int = int(os.getenv("ACCESS_TOKEN_MINUTES", "30"))
    refresh_token_days: int = int(os.getenv("REFRESH_TOKEN_DAYS", "7"))
    cors_origins: str = os.getenv(
        "CORS_ORIGINS",
        _default_dev_origins if _environment.lower() != "production" else "",
    )
    seed_demo_data: bool = os.getenv("SEED_DEMO_DATA", "true").lower() in {"1", "true", "yes"}

    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    def validate(self) -> None:
        if self.environment.lower() == "production" and self.secret_key == DEV_SECRET:
            raise RuntimeError("SECRET_KEY must be set to a strong non-default value in production")
        if self.environment.lower() == "production" and not self.allowed_origins:
            raise RuntimeError("CORS_ORIGINS must be set to explicit production origins")
        if "*" in self.allowed_origins:
            raise RuntimeError("CORS_ORIGINS must be an explicit allowlist; wildcard origins are not allowed")


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.validate()
    return settings
