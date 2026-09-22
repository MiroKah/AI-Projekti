# =============================================================================
# Infrastructure — Tekstin pilkkominen chunkkeihin (overlap-ikkuna)
# Toteuttaa TextChunker-portin. Varsinainen logiikka lisätään seuraavassa vaiheessa.
# =============================================================================
from __future__ import annotations

from app.core.config import settings
from app.domain.interfaces.services import TextChunker


class SimpleTextChunker(TextChunker):
    """Pilkkoo tekstin kiinteän kokoisiin paloihin, joissa on overlap."""

    def __init__(self, chunk_size: int | None = None, overlap: int | None = None) -> None:
        self.chunk_size = chunk_size or settings.CHUNK_SIZE
        self.overlap = overlap or settings.CHUNK_OVERLAP

    def chunk(self, text: str) -> list[str]:
        """Palauttaa listan tekstinpaloja. Toteutus lisätään seuraavassa vaiheessa."""
        raise NotImplementedError("Toteutetaan seuraavassa vaiheessa")