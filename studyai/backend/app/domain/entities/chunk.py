# =============================================================================
# Domain — Chunk-entiteetti
# Yksi tekstinpalanen dokumentista + sen embedding-vektori.
# =============================================================================
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID


@dataclass(slots=True)
class Chunk:
    """Pilkottu tekstinpalanen, johon liittyy embedding."""

    id: UUID
    document_id: UUID
    chunk_index: int
    content: str
    token_count: int | None = None
    # Embedding-vektori (float-lista); sama ulottuvuus kuin asetuksissa (oletus 1536)
    embedding: list[float] | None = field(default=None, repr=False)
    created_at: datetime | None = None