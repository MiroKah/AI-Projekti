# =============================================================================
# Infrastructure — DocumentRepository: toteuttaa domain-portin (PostgreSQL)
# =============================================================================
from __future__ import annotations

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.document import Document, DocumentStatus
from app.domain.interfaces.repositories import DocumentRepository
from app.infrastructure.database.models import DocumentModel


def _to_entity(model: DocumentModel) -> Document:
    """Muunna ORM-malli domain-entiteetiksi."""
    return Document(
        id=model.id,
        filename=model.filename,
        title=model.title,
        page_count=model.page_count,
        size_bytes=model.size_bytes,
        status=DocumentStatus(model.status),
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


class SqlDocumentRepository(DocumentRepository):
    """PostgreSQL-toteutus dokumenttirepositoriolle."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, document: Document) -> Document:
        model = DocumentModel(
            id=document.id,
            filename=document.filename,
            title=document.title,
            page_count=document.page_count,
            size_bytes=document.size_bytes,
            status=document.status.value,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return _to_entity(model)

    async def get(self, document_id: UUID) -> Document | None:
        model = await self._session.get(DocumentModel, document_id)
        return _to_entity(model) if model else None

    async def list(self) -> Sequence[Document]:
        result = await self._session.execute(
            select(DocumentModel).order_by(DocumentModel.created_at.desc())
        )
        return [_to_entity(m) for m in result.scalars().all()]

    async def update(self, document: Document) -> Document:
        model = await self._session.get(DocumentModel, document.id)
        if model is None:
            raise ValueError("Dokumenttia ei löytynyt")
        model.title = document.title
        model.page_count = document.page_count
        model.status = document.status.value
        await self._session.flush()
        await self._session.refresh(model)
        return _to_entity(model)

    async def delete(self, document_id: UUID) -> None:
        await self._session.execute(
            delete(DocumentModel).where(DocumentModel.id == document_id)
        )
        await self._session.flush()