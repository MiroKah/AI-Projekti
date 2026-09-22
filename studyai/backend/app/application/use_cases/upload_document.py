# =============================================================================
# Use case — PDF-dokumentin lataus ja käsittely (RAG-indeksointi)
#
# Vastuut (toteutetaan myöhemmin):
#   1. Validoi tiedosto (koko, tyyppi)
#   2. Tallenna dokumentin metatiedot
#   3. Purkaa PDF tekstiksi (PDFService)
#   4. Pilkkoo teksti chunkeiksi (TextChunker)
#   5. Luo embeddingit (EmbeddingService)
#   6. Tallenna chunkit + vektorit (ChunkRepository)
# =============================================================================
from __future__ import annotations

from app.core.logging import get_logger
from app.domain.interfaces.repositories import ChunkRepository, DocumentRepository
from app.domain.interfaces.services import EmbeddingService, PDFService, TextChunker

logger = get_logger(__name__)


class UploadDocumentUseCase:
    """Käsittelee PDF-tiedoston latauksen ja indeksoinnin vektorikantaan."""

    def __init__(
        self,
        *,
        document_repository: DocumentRepository,
        chunk_repository: ChunkRepository,
        pdf_service: PDFService,
        text_chunker: TextChunker,
        embedding_service: EmbeddingService,
    ) -> None:
        self._documents = document_repository
        self._chunks = chunk_repository
        self._pdf = pdf_service
        self._chunker = text_chunker
        self._embeddings = embedding_service

    async def execute(self, *, filename: str, file_bytes: bytes, title: str | None = None):
        """Suorita lataus ja indeksointi. Toteutus lisätään seuraavassa vaiheessa."""
        raise NotImplementedError("Toteutetaan seuraavassa vaiheessa")