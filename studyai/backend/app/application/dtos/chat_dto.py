# =============================================================================
# Application DTO — keskusteluun liittyvät siirto-oliot
# =============================================================================
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.domain.entities.chat import ChatMessage, SourceReference


class SourceDTO(BaseModel):
    """Lähdeviittaus API-vastauksessa."""

    chunk_id: UUID
    document_id: UUID
    chunk_index: int
    snippet: str = ""
    score: float | None = None

    @classmethod
    def from_entity(cls, source: SourceReference) -> "SourceDTO":
        """Muunna domain-lähde DTO:ksi."""
        return cls(
            chunk_id=source.chunk_id,
            document_id=source.document_id,
            chunk_index=source.chunk_index,
            snippet=source.snippet,
            score=source.score,
        )


class ChatMessageDTO(BaseModel):
    """Yksittäinen viesti API-vastauksessa."""

    id: UUID
    session_id: UUID
    role: str
    content: str
    sources: list[SourceDTO] = Field(default_factory=list)
    created_at: datetime | None = None

    @classmethod
    def from_entity(cls, message: ChatMessage) -> "ChatMessageDTO":
        """Muunna domain-viesti DTO:ksi."""
        return cls(
            id=message.id,
            session_id=message.session_id,
            role=message.role.value,
            content=message.content,
            sources=[SourceDTO.from_entity(s) for s in message.sources],
            created_at=message.created_at,
        )


class ChatRequestDTO(BaseModel):
    """Sisääntuleva chat-pyyntö."""

    question: str = Field(min_length=1, max_length=4000)
    document_id: UUID | None = None
    session_id: UUID | None = None


class ChatResponseDTO(BaseModel):
    """Chat-vastaus: assistentin viesti + lähteet."""

    session_id: UUID
    message: ChatMessageDTO