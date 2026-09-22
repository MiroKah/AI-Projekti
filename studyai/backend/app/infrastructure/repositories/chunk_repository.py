# =============================================================================
# Infrastructure — ChunkRepository: chunkit + pgvector-vektorihaku
# =============================================================================
from __future__ import annotations

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.chunk import Chunk
from app.domain.interfaces.repositories import ChunkRepository
from app.infrastructure.database.models import ChunkModel


def _to_entity(model: ChunkModel) -> Chunk:
    """Muunna ORM-malli domain-entiteetiksi (embedding jätetään pois keveyden vuoksi)."""
    return Chunk(
        id=model.id,
        document_id=model.document_id,
        chunk_index=model.chunk_index,
        content=model.content,
        token_count=model.token_count,
        embedding=None,
        created_at=model.created_at,
    )


class SqlChunkRepository(ChunkRepository):
    """PostgreSQL + pgvector -toteutus chunkkirepositoriolle."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add_many(self, chunks: Sequence[Chunk]) -> None:
        models = [
            ChunkModel(
                id=c.id,
                document_id=c.document_id,
                chunk_index=c.chunk_index,
                content=c.content,
                token_count=c.token_count,
                embedding=c.embedding,
            )
            for c in chunks
        ]
        self._session.add_all(models)
        await self._session.flush()

    async def delete_by_document(self, document_id: UUID) -> None:
        await self._session.execute(
            delete(ChunkModel).where(ChunkModel.document_id == document_id)
        )
        await self._session.flush()

    async def similarity_search(
        self,
        query_embedding: list[float],
        *,
        document_id: UUID | None = None,
        top_k: int = 5,
    ) -> Sequence[tuple[Chunk, float]]:
        # Kosinietäisyys: mitä pienempi, sitä lähempänä. Muunnetaan pisteeksi (1 - etäisyys).
        distance = ChunkModel.embedding.cosine_distance(query_embedding)
        statement = select(ChunkModel, distance.label("distance"))
        if document_id is not None:
            statement = statement.where(ChunkModel.document_id == document_id)
        statement = statement.order_by(distance).limit(top_k)

        result = await self._session.execute(statement)
        return [(_to_entity(row[0]), 1.0 - float(row[1])) for row in result.all()]