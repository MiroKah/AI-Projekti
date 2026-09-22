# =============================================================================
# Domain — Document-entiteetti ja sen tilat
# Puhdas liiketoimintalogiikka; ei riippuvuuksia tietokantaan tai kehykseen.
# =============================================================================
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID


class DocumentStatus(StrEnum):
    """Dokumentin käsittelyn tilat."""

    PENDING = "pending"          # Ladattu, ei vielä käsitelty
    PROCESSING = "processing"    # Tekstin purku / upotus käynnissä
    READY = "ready"              # Valmis keskusteluun
    FAILED = "failed"            # Käsittely epäonnistui


@dataclass(slots=True)
class Document:
    """Ladattu PDF-dokumentti ja sen metatiedot."""

    id: UUID
    filename: str
    title: str | None = None
    page_count: int | None = None
    size_bytes: int | None = None
    status: DocumentStatus = DocumentStatus.PENDING
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def mark_processing(self) -> None:
        """Merkitse dokumentti käsiteltäväksi."""
        self.status = DocumentStatus.PROCESSING

    def mark_ready(self, page_count: int | None = None) -> None:
        """Merkitse dokumentti valmiiksi; aseta sivumäärä jos tiedossa."""
        if page_count is not None:
            self.page_count = page_count
        self.status = DocumentStatus.READY

    def mark_failed(self) -> None:
        """Merkitse dokumentin käsittely epäonnistuneeksi."""
        self.status = DocumentStatus.FAILED

    @property
    def is_ready(self) -> bool:
        """Onko dokumentti valmis keskusteluun."""
        return self.status == DocumentStatus.READY