from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_ENV_FILE = Path(__file__).resolve().parents[2] / ".env"
APP_NAME = "Exercise Tracker API"
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7


class Settings(BaseSettings):
    database_url: str
    cors_origins: str | list[str] = []
    cors_allow_all: bool = False
    google_client_id: str = ""
    jwt_secret: str
    secure_cookies: bool = False
    cookie_samesite: str = "lax"
    allow_dev_auth: bool = True
    dev_user_email: str = "dev@example.com"
    dev_user_name: str = "Local Developer"

    model_config = SettingsConfigDict(env_file=ROOT_ENV_FILE, env_file_encoding="utf-8", extra="ignore")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @field_validator("cookie_samesite")
    @classmethod
    def validate_cookie_samesite(cls, value: str) -> str:
        normalized = value.lower()
        if normalized not in {"lax", "strict", "none"}:
            raise ValueError("cookie_samesite must be one of: lax, strict, none")
        return normalized


settings = Settings()
