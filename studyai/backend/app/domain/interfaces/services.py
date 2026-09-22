# =============================================================================
# Domain-portit — palvelurajapinnat (AI, PDF, chunkkaus)
# Nämä ovat abstraktioita ulkoisista palveluista, jotka infrastruktuuri toteuttaa.
# =============================================================================
from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence


class EmbeddingService(ABC):
    """Rajapinta tekstin upottamiseksi vektoreiksi."""

    @abstractmethod
    async def embed_text(self, text: str) -> list[float]:
        """Luo embedding yhdelle tekstille."""

    @abstractmethod
    async def embed_batch(self, texts: Sequence[str]) -> list[list[float]]:
        """Luo embeddingit usealle tekstille kerralla."""


class LLMService(ABC):
    """Rajapinta kielimallin kutsumiseksi (vastauksen generointi)."""

    @abstractmethod
    async def generate_answer(self, *, question: str, context: str) -> str:
        """Generoi vastaus annetun kontekstin perusteella."""


class PDFService(ABC):
    """Rajapinta PDF-tiedoston tekstin purkamiseksi."""

    @abstractmethod
    async def extract_text(self, file_bytes: bytes) -> tuple[str, int]:
        """Purkaa PDF:n tekstiksi. Palauttaa (teksti, sivumäärä)."""


class TextChunker(ABC):
    """Rajapinta tekstin pilkkomiseksi chunkeiksi."""

    @abstractmethod
    def chunk(self, text: str) -> list[str]:
        """Pilkoo tekstin palasiksi (overlap huomioiden)."""