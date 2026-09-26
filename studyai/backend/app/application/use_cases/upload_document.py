# =============================================================================
# Use case — PDF-dokumentin lataus ja käsittely (RAG-indeksointi)
#
# Vastuut:
#   1. Validoi tiedosto (koko, tyyppi) — PDFService tarkistaa koon/kelvollisuuden
#   2. Tallenna dokumentin metatiedot (DocumentRepository, tila: pending)
#   3. Purkaa PDF tekstiksi (PDFService)
#   4. Pilkkoo teksti chunkeiksi (TextChunker; chunk_size=1000, overlap=200)
#   5. Luo embeddingit (EmbeddingService; text-embedding-3-small)
#   6. Tallenna chunkit + vektorit (ChunkRepository, pgvector)
#   7. Merkitse dokumentti valmiiksi (tila: ready) — tai epäonnistuneeksi virheessä
# =============================================================================
from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4

from app.core.exceptions import FileProcessingError
from app.core.logging import get_logger
from app.domain.entities.chunk import Chunk
from app.domain.entities.document import Document
from app.domain.interfaces.repositories import ChunkRepository, DocumentRepository
from app.domain.interfaces.services import EmbeddingService, PDFService, TextChunker

logger = get_logger(__name__)


@dataclass(slots=True)
class IndexDocumentResult:
    """Indeksoinnin tulos: valmis dokumentti ja luotujen chunkkien määrä."""

    document: Document
    chunks_created: int


class UploadDocumentUseCase:
    """Käsittelee PDF-tiedoston latauksen ja indeksoinnin vektorikantaan (RAG)."""

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

    async def execute(
        self, *, filename: str, file_bytes: bytes, title: str | None = None
    ) -> IndexDocumentResult:
        """Suorittaa koko RAG-indeksointiputken yhdelle PDF-tiedostolle.

        Vaiheet: tallenna metatiedot → pura teksti → pilko chunkeiksi →
        luo embeddingit → tallenna chunkit → merkitse dokumentti valmiiksi.

        Jos jokin vaihe epäonnistuu tekstin purun jälkeen, dokumentti
        merkitään tilaan ``failed`` ja alkuperäinen poikkeus heitetään uudelleen.
        """
        document = Document(
            id=uuid4(),
            filename=filename,
            title=title,
            size_bytes=len(file_bytes),
        )
        document = await self._documents.add(document)
        logger.info("Dokumentti tallennettu (id=%s, filename=%s)", document.id, filename)

        document.mark_processing()
        document = await self._documents.update(document)

        try:
            chunks_created = await self._process_and_index(document, file_bytes)
        except Exception:
            logger.exception("Dokumentin indeksointi epäonnistui (id=%s)", document.id)
            document.mark_failed()
            await self._documents.update(document)
            raise

        return IndexDocumentResult(document=document, chunks_created=chunks_created)

    async def _process_and_index(self, document: Document, file_bytes: bytes) -> int:
        """Purkaa tekstin, pilkkoo, luo embeddingit, tallentaa ja merkitsee valmiiksi.

        Palauttaa luotujen chunkkien määrän. Päivittää ``document``-olion
        (sivumäärä + tila ``ready``) paikan päällä.
        """
        # 3. Pura PDF tekstiksi
        text, page_count = await self._pdf.extract_text(file_bytes)

        # 4. Pilko teksti chunkeiksi (chunk_size / overlap konfiguroitu chunkerissa)
        pieces = self._chunker.chunk(text)
        if not pieces:
            raise FileProcessingError("Dokumentista ei löytynyt pilkottavaa sisältöä")
        logger.info("Teksti pilkottu %s chunkiksi (document_id=%s)", len(pieces), document.id)

        # 5. Luo embeddingit kaikille chunkeille (erässä)
        embeddings = await self._embeddings.embed_batch(pieces)

        # 6. Rakenna Chunk-entiteetit ja tallenna pgvectoriin
        chunks = [
            Chunk(
                id=uuid4(),
                document_id=document.id,
                chunk_index=index,
                content=piece,
                token_count=len(piece.split()),
                embedding=embedding,
            )
            for index, (piece, embedding) in enumerate(zip(pieces, embeddings, strict=True))
        ]
        await self._chunks.add_many(chunks)
        logger.info("%s chunkkia tallennettu embeddingeineen (document_id=%s)", len(chunks), document.id)

        # 7. Merkitse dokumentti valmiiksi (sivumäärä tiedossa vasta tässä vaiheessa)
        document.mark_ready(page_count=page_count)
        await self._documents.update(document)

        return len(chunks)