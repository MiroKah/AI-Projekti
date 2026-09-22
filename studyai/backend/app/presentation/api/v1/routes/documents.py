# =============================================================================
# Presentation — dokumenttireitit (lataus, listaus, haku, poisto)
# HUOM: Varsinainen käsittelijälogiikka lisätään seuraavassa vaiheessa.
# =============================================================================
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.application.dtos.document_dto import DocumentDTO, DocumentListDTO, UploadResultDTO

router = APIRouter()


@router.post(
    "",
    response_model=UploadResultDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Lataa PDF-dokumentti",
)
async def upload_document(
    file: UploadFile = File(..., description="Ladattava PDF-tiedosto"),
) -> UploadResultDTO:
    """Vastaanottaa PDF:n, purkaa tekstin ja indeksoi sen vektorikantaan."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Toteutetaan seuraavassa vaiheessa",
    )


@router.get("", response_model=DocumentListDTO, summary="Listaa dokumentit")
async def list_documents() -> DocumentListDTO:
    """Palauttaa kaikki ladatut dokumentit."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Toteutetaan seuraavassa vaiheessa",
    )


@router.get("/{document_id}", response_model=DocumentDTO, summary="Hae dokumentti")
async def get_document(document_id: UUID) -> DocumentDTO:
    """Palauttaa yksittäisen dokumentin tiedot."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Toteutetaan seuraavassa vaiheessa",
    )


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Poista dokumentti",
)
async def delete_document(document_id: UUID) -> None:
    """Poistaa dokumentin ja siihen liittyvät chunkit."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Toteutetaan seuraavassa vaiheessa",
    )