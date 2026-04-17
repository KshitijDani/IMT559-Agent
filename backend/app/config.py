from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Exercise Tracker API"
    database_url: str = "postgresql+psycopg://exercise_user:exercise_pass@localhost:5432/exercise_tracker"
    cors_origins: list[str] = ["http://localhost:5173"]
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

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

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
