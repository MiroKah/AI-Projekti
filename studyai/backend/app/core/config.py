# =============================================================================
# Core — sovelluksen konfiguraatio (Pydantic Settings)
# Kaikki ympäristömuuttujat luetaan ja validoidaan tässä.
# =============================================================================
from __future__ import annotations

from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Sovelluksen asetukset (luetaan .env-tiedostosta)."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Sovellus ---
    APP_NAME: str = "StudyAI"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_PREFIX: str = "/api"

    # --- CORS: pilkkueroteltu lista sallituista origenista ---
    CORS_ORIGINS: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])

    # --- Tietokanta ---
    DATABASE_URL: str = "postgresql+asyncpg://studyai:studyai@localhost:5432/studyai"

    # --- OpenAI ---
    OPENAI_API_KEY: str = ""
    OPENAI_CHAT_MODEL: str = "gpt-4o-mini"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    OPENAI_EMBEDDING_DIMENSIONS: int = 1536

    # --- RAG-parametrit ---
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    RETRIEVAL_TOP_K: int = 5

    # --- Tiedostojen lataus ---
    MAX_UPLOAD_SIZE_MB: int = 25
    UPLOAD_DIR: str = "./data/uploads"

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def _split_cors_origins(cls, value: object) -> object:
        """Muunna pilkkueroteltu merkkijono listaksi."""
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @property
    def max_upload_size_bytes(self) -> int:
        """Maksimitiedostokoko tavuina."""
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    @property
    def is_production(self) -> bool:
        """Onko sovellus tuotantotilassa."""
        return self.APP_ENV.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    """Palauttaa välimuistiin tallennetun asetusinstanssin (singleton)."""
    return Settings()


# Koko sovelluksessa käytettävä asetusinstanssi
settings = get_settings()