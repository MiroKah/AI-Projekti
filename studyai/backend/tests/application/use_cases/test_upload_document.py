# =============================================================================
# Testit — UploadDocumentUseCase (RAG-indeksointiputki, fake-riippuvuudet)
# =============================================================================
from __future__ import annotations

from collections.abc import Sequence
from uuid import UUID

import pytest
from app.application.use_cases.upload_document import UploadDocumentUseCase
from app.core.exceptions import FileProcessingError
from app.domain.entities.chunk import Chunk
from app.domain.entities.document import Document, DocumentStatus


class FakeDocumentRepository:
    """Muistinvarainen DocumentRepository-fake testejä varten."""

    def __init__(self) -> None:
        self.saved: dict[UUID, Document] = {}
        self.status_history: list[DocumentStatus] = []

    async def add(self, document: Document) -> Document:
        self.saved[document.id] = document
        self.status_history.append(document.status)
        return document

    async def get(self, document_id: UUID) -> Document | None:
        return self.saved.get(document_id)

    async def list(self) -> Sequence[Document]:
        return list(self.saved.values())

    async def update(self, document: Document) -> Document:
        self.saved[document.id] = document
        self.status_history.append(document.status)
        return document

    async def delete(self, document_id: UUID) -> None:
        self.saved.pop(document_id, None)


class FakeChunkRepository:
    """Muistinvarainen ChunkRepository-fake testejä varten."""

    def __init__(self) -> None:
        self.added: list[Chunk] = []

    async def add_many(self, chunks: Sequence[Chunk]) -> None:
        self.added.extend(chunks)

    async def delete_by_document(self, document_id: UUID) -> None:
        self.added = [c for c in self.added if c.document_id != document_id]

    async def similarity_search(
        self, query_embedding: list[float], *, document_id: UUID | None = None, top_k: int = 5
    ) -> Sequence[tuple[Chunk, float]]:
        return []


class FakePDFService:
    """Palauttaa ennalta määrätyn tekstin ja sivumäärän."""

    def __init__(self, text: str = "Testidokumentin sisältö.", page_count: int = 3) -> None:
        self._text = text
        self._page_count = page_count

    async def extract_text(self, file_bytes: bytes) -> tuple[str, int]:
        return self._text, self._page_count


class FailingPDFService:
    """Simuloi PDF-purun epäonnistumista."""

    async def extract_text(self, file_bytes: bytes) -> tuple[str, int]:
        raise FileProcessingError("PDF-tiedosto on vioittunut")


class FakeTextChunker:
    """Palauttaa ennalta määrätyn listan chunkkeja riippumatta syötteestä."""

    def __init__(self, pieces: list[str] | None = None) -> None:
        self._pieces = pieces if pieces is not None else ["chunk-1", "chunk-2", "chunk-3"]

    def chunk(self, text: str) -> list[str]:
        return self._pieces


class FakeEmbeddingService:
    """Palauttaa deterministisen (lyhyen) embedding-vektorin per teksti."""

    def __init__(self) -> None:
        self.batch_calls: list[list[str]] = []

    async def embed_text(self, text: str) -> list[float]:
        return [float(len(text))]

    async def embed_batch(self, texts):
        self.batch_calls.append(list(texts))
        return [[float(len(t)), 0.0] for t in texts]


def _build_use_case(
    *,
    document_repository: FakeDocumentRepository,
    chunk_repository: FakeChunkRepository,
    embedding_service: FakeEmbeddingService,
    pdf_service=None,
    text_chunker=None,
) -> UploadDocumentUseCase:
    return UploadDocumentUseCase(
        document_repository=document_repository,
        chunk_repository=chunk_repository,
        pdf_service=pdf_service or FakePDFService(),
        text_chunker=text_chunker or FakeTextChunker(),
        embedding_service=embedding_service,
    )


class TestUploadDocumentUseCaseSuccess:
    """Onnistuneen indeksoinnin tarkistukset."""

    async def test_returns_document_marked_ready_with_page_count(
        self, document_repository, chunk_repository, embedding_service
    ) -> None:
        use_case = _build_use_case(
            document_repository=document_repository,
            chunk_repository=chunk_repository,
            embedding_service=embedding_service,
        )

        result = await use_case.execute(filename="kirja.pdf", file_bytes=b"%PDF-1.4 ...")

        assert result.document.status == DocumentStatus.READY
        assert result.document.page_count == 3
        assert result.document.filename == "kirja.pdf"

    async def test_creates_one_chunk_per_piece_with_matching_embeddings(
        self, document_repository, chunk_repository, embedding_service
    ) -> None:
        use_case = _build_use_case(
            document_repository=document_repository,
            chunk_repository=chunk_repository,
            embedding_service=embedding_service,
            text_chunker=FakeTextChunker(["a", "bb", "ccc"]),
        )

        result = await use_case.execute(filename="doc.pdf", file_bytes=b"bytes")

        assert result.chunks_created == 3
        assert len(chunk_repository.added) == 3
        assert [c.chunk_index for c in chunk_repository.added] == [0, 1, 2]
        assert [c.content for c in chunk_repository.added] == ["a", "bb", "ccc"]
        assert all(c.embedding is not None for c in chunk_repository.added)

    async def test_all_saved_chunks_reference_the_same_document_id(
        self, document_repository, chunk_repository, embedding_service
    ) -> None:
        use_case = _build_use_case(
            document_repository=document_repository,
            chunk_repository=chunk_repository,
            embedding_service=embedding_service,
        )

        result = await use_case.execute(filename="doc.pdf", file_bytes=b"bytes")

        assert all(c.document_id == result.document.id for c in chunk_repository.added)

    async def test_document_status_progresses_pending_processing_ready(
        self, document_repository, chunk_repository, embedding_service
    ) -> None:
        use_case = _build_use_case(
            document_repository=document_repository,
            chunk_repository=chunk_repository,
            embedding_service=embedding_service,
        )

        await use_case.execute(filename="doc.pdf", file_bytes=b"bytes")

        assert document_repository.status_history == [
            DocumentStatus.PENDING,
            DocumentStatus.PROCESSING,
            DocumentStatus.READY,
        ]

    async def test_embeddings_are_requested_for_all_chunk_pieces_in_one_batch(
        self, document_repository, chunk_repository, embedding_service
    ) -> None:
        pieces = ["p1", "p2", "p3", "p4"]
        use_case = _build_use_case(
            document_repository=document_repository,
            chunk_repository=chunk_repository,
            embedding_service=embedding_service,
            text_chunker=FakeTextChunker(pieces),
        )

        await use_case.execute(filename="doc.pdf", file_bytes=b"bytes")

        assert embedding_service.batch_calls == [pieces]


# -----------------------------------------------------------------------------
# Fixturet
# -----------------------------------------------------------------------------


@pytest.fixture
def document_repository() -> FakeDocumentRepository:
    return FakeDocumentRepository()


@pytest.fixture
def chunk_repository() -> FakeChunkRepository:
    return FakeChunkRepository()


@pytest.fixture
def embedding_service() -> FakeEmbeddingService:
    return FakeEmbeddingService()


class TestUploadDocumentUseCaseFailure:
    """Virhetilanteiden tarkistukset: dokumentti merkitään 'failed'."""

    async def test_pdf_extraction_failure_marks_document_failed_and_reraises(
        self, document_repository, chunk_repository, embedding_service
    ) -> None:
        use_case = _build_use_case(
            document_repository=document_repository,
            chunk_repository=chunk_repository,
            embedding_service=embedding_service,
            pdf_service=FailingPDFService(),
        )

        with pytest.raises(FileProcessingError):
            await use_case.execute(filename="broken.pdf", file_bytes=b"not-a-pdf")

        saved_documents = list(document_repository.saved.values())
        assert len(saved_documents) == 1
        assert saved_documents[0].status == DocumentStatus.FAILED

    async def test_no_chunks_saved_when_pdf_extraction_fails(
        self, document_repository, chunk_repository, embedding_service
    ) -> None:
        use_case = _build_use_case(
            document_repository=document_repository,
            chunk_repository=chunk_repository,
            embedding_service=embedding_service,
            pdf_service=FailingPDFService(),
        )

        with pytest.raises(FileProcessingError):
            await use_case.execute(filename="broken.pdf", file_bytes=b"not-a-pdf")

        assert chunk_repository.added == []

    async def test_empty_chunker_result_marks_document_failed(
        self, document_repository, chunk_repository, embedding_service
    ) -> None:
        use_case = _build_use_case(
            document_repository=document_repository,
            chunk_repository=chunk_repository,
            embedding_service=embedding_service,
            text_chunker=FakeTextChunker([]),
        )

        with pytest.raises(FileProcessingError):
            await use_case.execute(filename="empty.pdf", file_bytes=b"bytes")

        saved_documents = list(document_repository.saved.values())
        assert saved_documents[0].status == DocumentStatus.FAILED
