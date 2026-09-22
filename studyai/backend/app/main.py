# =============================================================================
# StudyAI Backend — FastAPI-sovelluksen käynnistys
# Kokoaa yhteen reitit, CORS-asetukset, poikkeuskäsittelijät ja lifespan-logiikan.
# =============================================================================
from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import configure_logging, get_logger
from app.presentation.api.v1.router import api_router
from app.presentation.middleware import register_exception_handlers

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Sovelluksen elinkaari: alustus käynnistyksessä ja siivous sammutuksessa."""
    configure_logging()
    logger.info("%s käynnistyy (ympäristö: %s)", settings.APP_NAME, settings.APP_ENV)
    yield
    logger.info("%s sammuu", settings.APP_NAME)


def create_app() -> FastAPI:
    """Luo ja konfiguroi FastAPI-sovelluksen."""
    app = FastAPI(
        title=settings.APP_NAME,
        description="RAG-sovellus: keskustele PDF-dokumenttien kanssa.",
        version="0.1.0",
        debug=settings.DEBUG,
        lifespan=lifespan,
    )

    # CORS: salli frontendin kutsut
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Poikkeuskäsittelijät
    register_exception_handlers(app)

    # API v1 -reitit
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    return app


app = create_app()