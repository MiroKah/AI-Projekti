# =============================================================================
# Domain-portit — repositorio-rajapinnat
# Abstraktit rajapinnat, jotka infrastruktuurikerros toteuttaa (dependency inversion).
# =============================================================================
from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from uuid import UUID

from app.domain.entities.chat import ChatMessage, ChatSession
from app.domain.entities.chunk import Chunk
from app.domain.entities.document import Document


class DocumentRepository(ABC):
    """Rajapinta dokumenttien tallennukseen ja hakuun."""

    @abstractmethod
    async def add(self, document: Document) -> Document:
        """Lisää uusi dokumentti."""

    @abstractmethod
    async def get(self, document_id: UUID) -> Document | None:
        """Hae dokumentti tunnisteella."""

    @abstractmethod
    async def list(self) -> Sequence[Document]:
        """Listaa kaikki dokumentit."""

    @abstractmethod
    async def update(self, document: Document) -> Document:
        """Päivitä olemassa oleva dokumentti."""

    @abstractmethod
    async def delete(self, document_id: UUID) -> None:
        """Poista dokumentti (ja siihen liittyvät chunkit kaskadilla)."""


class ChunkRepository(ABC):
    """Rajapinta chunkkien ja vektorihaun tallennukseen."""

    @abstractmethod
    async def add_many(self, chunks: Sequence[Chunk]) -> None:
        """Lisää useita chunkkeja kerralla."""

    @abstractmethod
    async def delete_by_document(self, document_id: UUID) -> None:
        """Poista dokumentin kaikki chunkit."""

    @abstractmethod
    async def similarity_search(
        self,
        query_embedding: list[float],
        *,
        document_id: UUID | None = None,
        top_k: int = 5,
    ) -> Sequence[tuple[Chunk, float]]:
        """Vektorihaku: palauttaa chunkit ja niiden samankaltaisuuspisteet."""


class ChatRepository(ABC):
    """Rajapinta keskusteluistuntojen ja viestien tallennukseen."""

    @abstractmethod
    async def create_session(self, session: ChatSession) -> ChatSession:
        """Luo uusi istunto."""

    @abstractmethod
    async def get_session(self, session_id: UUID) -> ChatSession | None:
        """Hae istunto tunnisteella."""

    @abstractmethod
    async def add_message(self, message: ChatMessage) -> ChatMessage:
        """Lisää viesti istuntoon."""

    @abstractmethod
    async def list_messages(self, session_id: UUID) -> Sequence[ChatMessage]:
        """Listaa istunnon viestit aikajärjestyksessä."""