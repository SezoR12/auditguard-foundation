from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    SYNC_DATABASE_URL: str | None = None
    JWT_SECRET: str
    SECRET_KEY: str = "change-me"
    REDIS_URL: str = "redis://redis:6379/0"
    JWT_ALG: str = "HS256"
    ACCESS_TOKEN_MINUTES: int = 30
    REFRESH_TOKEN_DAYS: int = 7
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()