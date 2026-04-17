from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Exercise Tracker API"
    database_url: str = "postgresql+psycopg://exercise_user:exercise_pass@localhost:5432/exercise_tracker"
    cors_origin: str = "http://localhost:5173"
    google_client_id: str = ""
    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7
    secure_cookies: bool = False
    allow_dev_auth: bool = True
    dev_user_email: str = "dev@example.com"
    dev_user_name: str = "Local Developer"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
