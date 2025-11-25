from __future__ import annotations

from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    PROJECT_NAME: str = "AI Interview Assistant API"
    VERSION: str = "1.0.0"
    APPLICATION_PORT: int = 8000
    DEBUG: bool = False

    DATABASE_URL: str

    JWT_SECRET: str
    JWT_ACCESS_TOKEN_TIME: str = "15m"
    JWT_REFRESH_TOKEN_TIME: str = "7d"
    JWT_ALGORITHM: str = "HS256"

    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    @property
    def allowed_origins_list(self) -> List[str]:
        """Преобразование строки origins в список."""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    ASSEMBLYAI_API_KEY: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
