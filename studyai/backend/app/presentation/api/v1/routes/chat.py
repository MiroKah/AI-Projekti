# =============================================================================
# Presentation — chat-reitti (RAG-kysely dokumentilta)
# HUOM: Varsinainen käsittelijälogiikka lisätään seuraavassa vaiheessa.
# =============================================================================
from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.application.dtos.chat_dto import ChatRequestDTO, ChatResponseDTO

router = APIRouter()


@router.post(
    "",
    response_model=ChatResponseDTO,
    summary="Kysy dokumentilta (RAG)",
)
async def chat(payload: ChatRequestDTO) -> ChatResponseDTO:
    """Vastaa kysymykseen dokumentin sisällön perusteella ja palauttaa lähteet."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Toteutetaan seuraavassa vaiheessa",
    )