# =============================================================================
# Infrastructure — OpenAI-palvelutoteutukset
# Toteuttaa EmbeddingService- ja LLMService-portit OpenAI:n API:a vasten.
# HUOM: Varsinainen logiikka lisätään seuraavassa vaiheessa.
# =============================================================================
from __future__ import annotations

from collections.abc import Sequence

from openai import AsyncOpenAI

from app.core.config import settings
from app.core.logging import get_logger
from app.domain.interfaces.services import EmbeddingService, LLMService

logger = get_logger(__name__)


class OpenAIEmbeddingService(EmbeddingService):
    """Luo tekstin upotukset OpenAI Embeddings -rajapinnalla."""

    def __init__(self, client: AsyncOpenAI | None = None) -> None:
        self._client = client or AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self._model = settings.OPENAI_EMBEDDING_MODEL
        self._dimensions = settings.OPENAI_EMBEDDING_DIMENSIONS

    async def embed_text(self, text: str) -> list[float]:
        raise NotImplementedError("Toteutetaan seuraavassa vaiheessa")

    async def embed_batch(self, texts: Sequence[str]) -> list[list[float]]:
        raise NotImplementedError("Toteutetaan seuraavassa vaiheessa")


class OpenAILLMService(LLMService):
    """Generoi vastauksia OpenAI Responses API:lla."""

    def __init__(self, client: AsyncOpenAI | None = None) -> None:
        self._client = client or AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self._model = settings.OPENAI_CHAT_MODEL

    async def generate_answer(self, *, question: str, context: str) -> str:
        raise NotImplementedError("Toteutetaan seuraavassa vaiheessa")