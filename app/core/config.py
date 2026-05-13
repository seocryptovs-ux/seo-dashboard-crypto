import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    COINGECKO_API_KEY: str = ""
    COINGECKO_PLAN: str = "pro"
    COINGECKO_TIMEOUT: int = 20

    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = int(os.getenv("PORT", "8000"))

    API_KEY: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()