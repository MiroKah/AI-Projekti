# =============================================================================
# Presentation — terveystarkistusreitti
# =============================================================================
from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from app.core.config import settings

router = APIRouter()


class HealthResponse(BaseModel):
    """Terveystarkistuksen vastaus."""

    status: str = "ok"
    app: str
    env: str
    version: str


@router.get("/health", response_model=HealthResponse, summary="Terveystarkistus")
async def health() -> HealthResponse:
    """Palauttaa sovelluksen tilan."""
    from app import __version__

    return HealthResponse(
        status="ok",
        app=settings.APP_NAME,
        env=settings.APP_ENV,
        version=__version__,
    )