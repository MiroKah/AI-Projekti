# =============================================================================
# Infrastructure — Tekstin pilkkominen chunkkeihin (overlap-ikkuna)
# Toteuttaa domain-portin TextChunker: liukuva merkkipohjainen ikkuna.
# Oletukset: chunk_size = 1000, chunk_overlap = 200 (ks. app.core.config).
# =============================================================================
from __future__ import annotations

from app.core.config import settings
from app.core.exceptions import ValidationError
from app.domain.interfaces.services import TextChunker


class SimpleTextChunker(TextChunker):
    """Pilkkoo tekstin kiinteän kokoisiin paloihin, joissa on overlap.

    Algoritmi on merkkipohjainen liukuva ikkuna:
      - Jokainen chunk on enintään ``chunk_size`` merkkiä pitkä.
      - Peräkkäiset chunkit limittyvät ``overlap`` merkillä, jotta konteksti
        ei katkea kappaleen rajalla (tärkeää RAG-hakutarkkuudelle).
      - Tyhjät/whitespace-only palat suodatetaan pois.
    """

    def __init__(self, chunk_size: int | None = None, overlap: int | None = None) -> None:
        self.chunk_size = chunk_size if chunk_size is not None else settings.CHUNK_SIZE
        self.overlap = overlap if overlap is not None else settings.CHUNK_OVERLAP

        if self.chunk_size <= 0:
            raise ValidationError("chunk_size on oltava positiivinen")
        if self.overlap < 0:
            raise ValidationError("chunk_overlap ei voi olla negatiivinen")
        if self.overlap >= self.chunk_size:
            raise ValidationError("chunk_overlap on oltava pienempi kuin chunk_size")

    def chunk(self, text: str) -> list[str]:
        """Pilkkoo tekstin liukuvalla ikkunalla (chunk_size, overlap huomioiden).

        Palauttaa listan siivottuja tekstinpaloja alkuperäisessä järjestyksessä.
        Tyhjä tai vain whitespacea sisältävä syöte palauttaa tyhjän listan.
        """
        cleaned = text.strip()
        if not cleaned:
            return []

        step = self.chunk_size - self.overlap
        text_length = len(cleaned)
        chunks: list[str] = []
        start = 0

        while start < text_length:
            end = min(start + self.chunk_size, text_length)
            piece = cleaned[start:end].strip()
            if piece:
                chunks.append(piece)
            if end >= text_length:
                break
            start += step

        return chunks