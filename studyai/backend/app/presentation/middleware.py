# =============================================================================
# Presentation — poikkeuskäsittelijät
# Muuntaa sovelluskohtaiset poikkeukset yhtenäisiksi HTTP-vastauksiksi.
# =============================================================================
from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.exceptions import StudyAIError
from app.core.logging import get_logger

logger = get_logger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    """Rekisteröi poikkeuskäsittelijät FastAPI-sovellukseen."""

    @app.exception_handler(StudyAIError)
    async def _handle_studyai_error(_: Request, exc: StudyAIError) -> JSONResponse:
        logger.warning("Sovellusvirhe: %s", exc.message)
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.__class__.__name__, "detail": exc.message},
        )