from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from urllib.parse import urlparse
from pathlib import Path

ROOT_ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    app_name: str = "Exercise Tracker API"
    database_url: str = "postgresql+psycopg://exercise_user:exercise_pass@localhost:5432/exercise_tracker"
    base_url: str = "https://headgear-grinch-credit.ngrok-free.dev/"
    cors_origins: list[str] = ["http://localhost:8000"]
    cors_allow_all: bool = False
    google_client_id: str = ""
    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7
    secure_cookies: bool = False
    cookie_samesite: str = "lax"
    allow_dev_auth: bool = True
    demo_no_auth: bool = True
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

    @field_validator("base_url")
    @classmethod
    def normalize_base_url(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("base_url must not be empty")
        return normalized.rstrip("/") + "/"

    @property
    def base_origin(self) -> str:
        parsed = urlparse(self.base_url)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError("base_url must include scheme and host")
        return f"{parsed.scheme}://{parsed.netloc}"


settings = Settings()
