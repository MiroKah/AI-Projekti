# =============================================================================
# Application DTO — dokumentteihin liittyvät siirto-oliot
# =============================================================================
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.domain.entities.document import Document, DocumentStatus


class DocumentDTO(BaseModel):
    """Julkinen esitys dokumentista (API-vastaus)."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    filename: str
    title: str | None = None
    page_count: int | None = None
    size_bytes: int | None = None
    status: DocumentStatus
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @classmethod
    def from_entity(cls, document: Document) -> DocumentDTO:
        """Muunna domain-entiteetti DTO:ksi."""
        return cls(
            id=document.id,
            filename=document.filename,
            title=document.title,
            page_count=document.page_count,
            size_bytes=document.size_bytes,
            status=document.status,
            created_at=document.created_at,
            updated_at=document.updated_at,
        )


class DocumentListDTO(BaseModel):
    """Lista dokumenteista."""

    items: list[DocumentDTO] = Field(default_factory=list)
    total: int = 0


class UploadResultDTO(BaseModel):
    """Tulos PDF-tiedoston latauksesta ja käsittelystä."""

    document: DocumentDTO
    chunks_created: int = 0
    message: str = "Dokumentti käsitelty onnistuneesti"