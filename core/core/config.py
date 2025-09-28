from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    SQLALCHEMY_DATABASE_URL: str = "sqlite:///./sqlite.db"
    JWT_SECRET_KEY: str = 'test'
    JWT_ALGORITHM: str = 'HS256'
    JWT_ACCESS_TOKEN_EXPIRES: int = 60 * 10
    JWT_REFRESH_TOKEN_EXPIRES: int = 60 * 60 * 24 * 30

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()
