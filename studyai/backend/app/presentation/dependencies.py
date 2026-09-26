# =============================================================================
# Presentation — riippuvuuksien injektointi (DI)
# Kokoaa domain-porttien toteutukset ja tarjoaa ne reiteille.
# =============================================================================
from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.chat_with_document import ChatWithDocumentUseCase
from app.application.use_cases.upload_document import UploadDocumentUseCase
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


# --- Use case:t ---
async def get_upload_document_use_case(
    document_repository: DocumentRepository = Depends(get_document_repository),
    chunk_repository: ChunkRepository = Depends(get_chunk_repository),
    pdf_service: PDFService = Depends(get_pdf_service),
    text_chunker: TextChunker = Depends(get_text_chunker),
    embedding_service: EmbeddingService = Depends(get_embedding_service),
) -> UploadDocumentUseCase:
    """Tarjoaa dokumentin lataus- ja indeksointi-use casen (RAG-putki)."""
    return UploadDocumentUseCase(
        document_repository=document_repository,
        chunk_repository=chunk_repository,
        pdf_service=pdf_service,
        text_chunker=text_chunker,
        embedding_service=embedding_service,
    )


async def get_chat_with_document_use_case(
    document_repository: DocumentRepository = Depends(get_document_repository),
    chunk_repository: ChunkRepository = Depends(get_chunk_repository),
    chat_repository: ChatRepository = Depends(get_chat_repository),
    embedding_service: EmbeddingService = Depends(get_embedding_service),
    llm_service: LLMService = Depends(get_llm_service),
) -> ChatWithDocumentUseCase:
    """Tarjoaa keskustelu-use casen (RAG-kysely: embedding → haku → konteksti → LLM)."""
    return ChatWithDocumentUseCase(
        document_repository=document_repository,
        chunk_repository=chunk_repository,
        chat_repository=chat_repository,
        embedding_service=embedding_service,
        llm_service=llm_service,
        retrieval_top_k=settings.RETRIEVAL_TOP_K,
    )