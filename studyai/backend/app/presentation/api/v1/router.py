# =============================================================================
# Presentation — API v1 -pääreititin
# Kokoaa yhteen kaikki v1-alireitittimet.
# =============================================================================
from __future__ import annotations

from fastapi import APIRouter

from app.presentation.api.v1.routes import chat, documents, health

api_router = APIRouter()

api_router.include_router(health.router, tags=["health"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])