# =============================================================================
# Use case — keskustelu dokumentin kanssa (RAG-kysely)
#
# Vaiheet (toteutetaan myöhemmin):
#   1. Luo embedding kysymykselle (EmbeddingService)
#   2. Vektorihaku: hae relevanteimmat chunkit (ChunkRepository)
#   3. Rakenna konteksti haetuista chunkeista
#   4. Generoi vastaus kontekstin perusteella (LLMService)
#   5. Tallenna käyttäjän viesti ja assistentin vastaus + lähteet (ChatRepository)
# =============================================================================
from __future__ import annotations

from uuid import UUID

from app.core.logging import get_logger
from app.domain.interfaces.repositories import (
    ChatRepository,
    ChunkRepository,
    DocumentRepository,
)
from app.domain.interfaces.services import EmbeddingService, LLMService

logger = get_logger(__name__)


class ChatWithDocumentUseCase:
    """Vastaa käyttäjän kysymykseen dokumentin sisällön perusteella (RAG)."""

    def __init__(
        self,
        *,
        document_repository: DocumentRepository,
        chunk_repository: ChunkRepository,
        chat_repository: ChatRepository,
        embedding_service: EmbeddingService,
        llm_service: LLMService,
        retrieval_top_k: int = 5,
    ) -> None:
        self._documents = document_repository
        self._chunks = chunk_repository
        self._chat = chat_repository
        self._embeddings = embedding_service
        self._llm = llm_service
        self._top_k = retrieval_top_k

    async def execute(
        self,
        *,
        question: str,
        document_id: UUID | None = None,
        session_id: UUID | None = None,
    ):
        """Suorita RAG-kysely. Toteutus lisätään seuraavassa vaiheessa."""
        raise NotImplementedError("Toteutetaan seuraavassa vaiheessa")