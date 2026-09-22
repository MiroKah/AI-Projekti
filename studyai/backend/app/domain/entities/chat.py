# =============================================================================
# Domain — Chat-entiteetit: istunto, viesti ja lähdeviittaus
# =============================================================================
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from uuid import UUID


class ChatRole(StrEnum):
    """Viestin rooli keskustelussa."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


@dataclass(slots=True)
class SourceReference:
    """Yksi lähdeviittaus (mihin dokumentin kohtaan vastaus perustuu)."""

    chunk_id: UUID
    document_id: UUID
    chunk_index: int
    # Lyhyt ote lähteestä, näytetään käyttöliittymässä
    snippet: str = ""
    # Samankaltaisuuspisteet (0..1), jos tiedossa
    score: float | None = None


@dataclass(slots=True)
class ChatMessage:
    """Yksittäinen viesti keskusteluistunnossa."""

    id: UUID
    session_id: UUID
    role: ChatRole
    content: str
    sources: list[SourceReference] = field(default_factory=list)
    created_at: datetime | None = None


@dataclass(slots=True)
class ChatSession:
    """Keskusteluistunto, joka on liitetty (valinnaisesti) yhteen dokumenttiin."""

    id: UUID
    document_id: UUID | None = None
    title: str | None = None
    created_at: datetime | None = None
    messages: list[ChatMessage] = field(default_factory=list)