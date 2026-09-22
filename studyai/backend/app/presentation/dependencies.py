# =============================================================================
# Presentation — riippuvuuksien injektointi (DI)
# Kokoaa domain-porttien toteutukset ja tarjoaa ne reiteille.
# =============================================================================
from __future__ import annotations

from collections.abc import AsyncIterator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.domain.interfaces.repositories import (
    ChatRepository,
    ChunkRepository,
    DocumentRepository,
)
from app.domain.interfaces.services import EmbeddingService, LLMService, PDFService, TextChunker
from app.infrastructure.database.session import get_session
from app.infrastructure.repositories.chat_repository import SqlChatRepository
from app.infrastructure.repositories.chunk_repository import SqlChunkRepository
from app.infrastructure.repositories.document_repository import SqlDocumentRepository
from app.infrastructure.services.openai_service import (
    OpenAIEmbeddingService,
    OpenAILLMService,
)
from app.infrastructure.services.pdf_service import PyMuPDFService
from app.infrastructure.services.text_chunker import SimpleTextChunker


# --- Tietokantarepositoriot (per pyyntö, sama istunto) ---
async def get_document_repository(
    session: AsyncSession = Depends(get_session),
) -> DocumentRepository:
    """Tarjoaa dokumenttirepositorion."""
    return SqlDocumentRepository(session)


async def get_chunk_repository(
    session: AsyncSession = Depends(get_session),
) -> ChunkRepository:
    """Tarjoaa chunkkirepositorion."""
    return SqlChunkRepository(session)


async def get_chat_repository(
    session: AsyncSession = Depends(get_session),
) -> ChatRepository:
    """Tarjoaa keskustelurepositorion."""
    return SqlChatRepository(session)


# --- Ulkoiset palvelut ---
async def get_embedding_service() -> EmbeddingService:
    """Tarjoaa embedding-palvelun."""
    return OpenAIEmbeddingService()


async def get_llm_service() -> LLMService:
    """Tarjoaa kielimallipalvelun."""
    return OpenAILLMService()


async def get_pdf_service() -> PDFService:
    """Tarjoaa PDF-palvelun."""
    return PyMuPDFService()


async def get_text_chunker() -> TextChunker:
    """Tarjoaa tekstinpilkkujan."""
    return SimpleTextChunker(
        chunk_size=settings.CHUNK_SIZE,
        overlap=settings.CHUNK_OVERLAP,
    )