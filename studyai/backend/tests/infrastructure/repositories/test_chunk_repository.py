# =============================================================================
# Testit — SqlChunkRepository.similarity_search (pgvector, top-k)
# Mockataan SQLAlchemy-istunto kevyesti (MagicMock-ketju); tarkistetaan erityisesti:
#   1. tulosten muunnos (score = 1 - cosine_distance)
#   2. SQL-kyselyn rakenne (LIMIT top_k, document_id-suodatin)
# =============================================================================
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from app.infrastructure.repositories.chunk_repository import SqlChunkRepository
from sqlalchemy.dialects import postgresql


def _build_chunk_row() -> MagicMock:
    """Rakentaa mockatun ChunkModel-rivin (_to_entity vaatii nämä kentät)."""
    row = MagicMock()
    row.id = uuid4()
    row.document_id = uuid4()
    row.chunk_index = 0
    row.content = "palanen sisältöä"
    row.token_count = 3
    row.created_at = None
    return row


def _make_session(rows: list) -> MagicMock:
    """Luo mock-istunnon: await session.execute(stmt) -> result, result.all() -> rivit."""
    session = MagicMock()
    result = MagicMock()
    result.all.return_value = rows
    session.execute = AsyncMock(return_value=result)
    return session


class TestSimilaritySearch:
    """Tarkistaa vektorihaku-logiikan ja top-k -rajoituksen."""

    async def test_returns_empty_list_when_no_results(self) -> None:
        session = _make_session([])
        repository = SqlChunkRepository(session)

        results = await repository.similarity_search([0.1] * 1536)

        assert results == []

    async def test_returns_chunk_and_score_pairs(self) -> None:
        session = _make_session([(_build_chunk_row(), 0.25)])
        repository = SqlChunkRepository(session)

        results = await repository.similarity_search([0.1] * 1536)

        assert len(results) == 1
        chunk, score = results[0]
        assert chunk.content == "palanen sisältöä"
        # score = 1 - cosine_distance (0.25 -> 0.75)
        assert score == pytest.approx(0.75)

    async def test_passes_top_k_to_query_limit(self) -> None:
        """Tarkistaa, että top_k=5 välitetään kyselyyn (LIMIT)."""
        session = _make_session([])
        repository = SqlChunkRepository(session)

        await repository.similarity_search([0.1] * 1536, top_k=5)

        statement = session.execute.call_args[0][0]
        # Kääritään SQL Postgres-dialektilla (literal_binds) ja tarkistetaan LIMIT
        compiled = str(
            statement.compile(
                dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True}
            )
        )
        assert "LIMIT 5" in compiled

    async def test_filters_by_document_id_when_provided(self) -> None:
        """Tarkistaa, että dokumentti-id-suojaus lisätään kyselyyn tarvittaessa."""
        session = _make_session([])
        repository = SqlChunkRepository(session)
        document_id = uuid4()

        await repository.similarity_search(
            [0.1] * 1536, document_id=document_id, top_k=5
        )

        statement = session.execute.call_args[0][0]
        whereclause = str(statement.whereclause)
        assert "document_id" in whereclause

    async def test_no_document_filter_when_not_provided(self) -> None:
        """Tarkistaa, että ei-suodatettua hakua ei rajata dokumenttiin."""
        session = _make_session([])
        repository = SqlChunkRepository(session)

        await repository.similarity_search([0.1] * 1536, top_k=5)

        statement = session.execute.call_args[0][0]
        assert statement.whereclause is None
