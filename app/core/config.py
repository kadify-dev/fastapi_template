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
    REFRESH_TOKEN_EXPIRE_MINUTES: int

    LOG_LEVEL: str = "ERROR"

    @property
    def ASYNC_DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def log_level(self) -> int:
        return getattr(logging, self.LOG_LEVEL, logging.ERROR)

    model_config = SettingsConfigDict(env_file=None, extra="ignore")


def get_settings() -> Settings:
    mode = os.getenv("APP_MODE", "dev")
    env_file = f".env.{mode}"

    if not os.path.exists(env_file):
        raise FileNotFoundError(f"Environment file {env_file} not found")

    return Settings(_env_file=env_file)


settings = get_settings()
