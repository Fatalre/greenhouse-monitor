from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    app_env: str = "development"
    app_name: str = "Greenhouse Monitor"
    app_version: str = "1.0.0"
    app_secret_key: str = "dev-secret-change-me"
    database_url: str = "sqlite:///./greenhouse.db"
    cors_origins: str = "http://localhost:5173"
    device_offline_threshold_seconds: int = 15
    max_request_body_bytes: int = 16384
    default_timezone: str = "Europe/Kyiv"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30
    rate_limit_measurements_per_minute: int = 120
    enable_openapi: bool = True
    admin_username: str = "admin"
    admin_password: str = "change-me"

    @property
    def cors_origin_list(self) -> list[str]:
        return [x.strip() for x in self.cors_origins.split(",") if x.strip()]

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
