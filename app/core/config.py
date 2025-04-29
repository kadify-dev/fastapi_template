import logging
import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int

    LOG_LEVEL: str = "ERROR"

    @property
    def ASYNC_DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def log_level(self) -> int:
        return getattr(logging, self.LOG_LEVEL, logging.ERROR)

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


def get_settings() -> Settings:
    if env_mode := os.getenv("APP_MODE"):
        env_file = f".env.{env_mode}"
        if os.path.exists(env_file):
            return Settings(_env_file=env_file)
    return Settings()


settings = get_settings()
