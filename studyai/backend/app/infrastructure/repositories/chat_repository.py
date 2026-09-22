# =============================================================================
# Infrastructure — ChatRepository: istunnot ja viestit (PostgreSQL)
# =============================================================================
from __future__ import annotations

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.chat import (
    ChatMessage,
    ChatRole,
    ChatSession,
    SourceReference,
)
from app.domain.interfaces.repositories import ChatRepository
from app.infrastructure.database.models import ChatMessageModel, ChatSessionModel


def _session_to_entity(model: ChatSessionModel) -> ChatSession:
    """Muunna istunto-malli domain-entiteetiksi."""
    return ChatSession(
        id=model.id,
        document_id=model.document_id,
        title=model.title,
        created_at=model.created_at,
    )


def _message_to_entity(model: ChatMessageModel) -> ChatMessage:
    """Muunna viesti-malli domain-entiteetiksi (lähteet JSONB:stä)."""
    sources = [
        SourceReference(
            chunk_id=UUID(s["chunk_id"]),
            document_id=UUID(s["document_id"]),
            chunk_index=int(s["chunk_index"]),
            snippet=s.get("snippet", ""),
            score=s.get("score"),
        )
        for s in (model.sources or [])
    ]
    return ChatMessage(
        id=model.id,
        session_id=model.session_id,
        role=ChatRole(model.role),
        content=model.content,
        sources=sources,
        created_at=model.created_at,
    )


class SqlChatRepository(ChatRepository):
    """PostgreSQL-toteutus keskustelurepositoriolle."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_session(self, session: ChatSession) -> ChatSession:
        model = ChatSessionModel(
            id=session.id,
            document_id=session.document_id,
            title=session.title,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return _session_to_entity(model)

    async def get_session(self, session_id: UUID) -> ChatSession | None:
        model = await self._session.get(ChatSessionModel, session_id)
        return _session_to_entity(model) if model else None

    async def add_message(self, message: ChatMessage) -> ChatMessage:
        model = ChatMessageModel(
            id=message.id,
            session_id=message.session_id,
            role=message.role.value,
            content=message.content,
            sources=[
                {
                    "chunk_id": str(s.chunk_id),
                    "document_id": str(s.document_id),
                    "chunk_index": s.chunk_index,
                    "snippet": s.snippet,
                    "score": s.score,
                }
                for s in message.sources
            ],
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return _message_to_entity(model)

    async def list_messages(self, session_id: UUID) -> Sequence[ChatMessage]:
        result = await self._session.execute(
            select(ChatMessageModel)
            .where(ChatMessageModel.session_id == session_id)
            .order_by(ChatMessageModel.created_at.asc())
        )
        return [_message_to_entity(m) for m in result.scalars().all()]