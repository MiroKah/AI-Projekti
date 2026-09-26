# =============================================================================
# Testit — SimpleTextChunker (chunk_size / chunk_overlap -pilkkoja)
# =============================================================================
from __future__ import annotations

import pytest
from app.core.exceptions import ValidationError
from app.infrastructure.services.text_chunker import SimpleTextChunker


class TestChunkerConstruction:
    """Testaa parametrien validointia rakentajassa."""

    def test_uses_default_settings_when_not_provided(self) -> None:
        chunker = SimpleTextChunker()
        assert chunker.chunk_size == 1000
        assert chunker.overlap == 200

    def test_rejects_non_positive_chunk_size(self) -> None:
        with pytest.raises(ValidationError):
            SimpleTextChunker(chunk_size=0, overlap=10)

    def test_rejects_negative_overlap(self) -> None:
        with pytest.raises(ValidationError):
            SimpleTextChunker(chunk_size=100, overlap=-1)

    def test_rejects_overlap_greater_or_equal_to_chunk_size(self) -> None:
        with pytest.raises(ValidationError):
            SimpleTextChunker(chunk_size=100, overlap=100)


class TestChunkBehavior:
    """Testaa varsinaista pilkkomislogiikkaa."""

    def test_empty_text_returns_empty_list(self) -> None:
        chunker = SimpleTextChunker(chunk_size=10, overlap=2)
        assert chunker.chunk("") == []

    def test_whitespace_only_returns_empty_list(self) -> None:
        chunker = SimpleTextChunker(chunk_size=10, overlap=2)
        assert chunker.chunk("   \n\t  ") == []

    def test_text_shorter_than_chunk_size_returns_single_chunk(self) -> None:
        chunker = SimpleTextChunker(chunk_size=1000, overlap=200)
        text = "Lyhyt teksti."
        assert chunker.chunk(text) == [text]

    def test_splits_long_text_into_multiple_chunks(self) -> None:
        chunker = SimpleTextChunker(chunk_size=10, overlap=2)
        text = "a" * 25
        chunks = chunker.chunk(text)
        assert len(chunks) > 1
        assert all(len(c) <= 10 for c in chunks)

    def test_consecutive_chunks_overlap_by_configured_amount(self) -> None:
        chunker = SimpleTextChunker(chunk_size=10, overlap=3)
        text = "0123456789ABCDEFGHIJ"  # 20 merkkiä
        chunks = chunker.chunk(text)
        # step = 10 - 3 = 7 -> chunkit alkavat indekseistä 0, 7, 14
        assert chunks[0] == "0123456789"
        assert chunks[1] == "789ABCDEFG"
        assert chunks[0][-3:] == chunks[1][:3]

    def test_default_1000_200_produces_expected_chunk_count(self) -> None:
        """Tehtävän vaatimat oletusarvot: chunk_size=1000, chunk_overlap=200."""
        chunker = SimpleTextChunker(chunk_size=1000, overlap=200)
        text = "x" * 2200
        chunks = chunker.chunk(text)
        # step = 800 -> alut: 0, 800, 1600 => 3 chunkia (viimeinen 600 merkkiä)
        assert len(chunks) == 3
        assert len(chunks[0]) == 1000
        assert len(chunks[1]) == 1000
        assert len(chunks[2]) == 600

    def test_no_content_is_lost_across_chunks(self) -> None:
        """Koko alkuperäinen teksti löytyy chunkkien yhdisteestä (overlap huomioiden)."""
        chunker = SimpleTextChunker(chunk_size=50, overlap=10)
        text = "".join(str(i % 10) for i in range(237))
        chunks = chunker.chunk(text)
        # Ensimmäinen chunk kattaa alun; viimeinen kattaa lopun
        assert text.startswith(chunks[0])
        assert text.endswith(chunks[-1])

    def test_strips_whitespace_from_each_piece(self) -> None:
        chunker = SimpleTextChunker(chunk_size=5, overlap=1)
        text = "ab   cd   ef   gh   ij"
        chunks = chunker.chunk(text)
        assert all(c == c.strip() for c in chunks)
        assert all(c for c in chunks)
