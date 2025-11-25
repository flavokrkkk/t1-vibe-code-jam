from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    PROJECT_NAME: str = "AI Interview Assistant API"
    VERSION: str = "1.0.0"
    APPLICATION_PORT: int = 8000
    DEBUG: bool = False
    BASE_URL: str = "http://localhost:8000"
    
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    JWT_SECRET: str
    JWT_ACCESS_TOKEN_TIME: int = 15
    JWT_REFRESH_TOKEN_TIME: int = 7
    JWT_ALGORITHM: str = "HS256"

    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    @property
    def allowed_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    ASSEMBLYAI_API_KEY: str | None = None

    ML_API_URL: str = "http://localhost:8080"

    model_config = SettingsConfigDict(
        env_file="../.env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
