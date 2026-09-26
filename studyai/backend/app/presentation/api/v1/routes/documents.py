# =============================================================================
# Presentation — dokumenttireitit (lataus, listaus, haku, poisto)
# Vastaa API-sopimuksesta: POST/GET /api/documents, GET/DELETE /api/documents/{id}
# =============================================================================
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, File, UploadFile, status

from app.application.dtos.document_dto import DocumentDTO, DocumentListDTO, UploadResultDTO
from app.application.use_cases.upload_document import UploadDocumentUseCase
from app.core.exceptions import NotFoundError
from app.domain.interfaces.repositories import DocumentRepository
from app.presentation.api.v1.routes._pdf_upload import read_pdf_bytes
from app.presentation.dependencies import (
    get_document_repository,
    get_upload_document_use_case,
)

router = APIRouter()


@router.post(
    "",
    response_model=UploadResultDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Lataa PDF-dokumentti",
)
async def upload_document(
    file: UploadFile = File(..., description="Ladattava PDF-tiedosto"),
    use_case: UploadDocumentUseCase = Depends(get_upload_document_use_case),
) -> UploadResultDTO:
    """Vastaanottaa PDF:n, purkaa tekstin ja indeksoi sen vektorikantaan."""
    file_bytes = await read_pdf_bytes(file)
    result = await use_case.execute(
        filename=file.filename or "document.pdf",
        file_bytes=file_bytes,
    )
    return UploadResultDTO(
        document=DocumentDTO.from_entity(result.document),
        chunks_created=result.chunks_created,
        message=f"Dokumentti käsitelty onnistuneesti ({result.chunks_created} chunkkia)",
    )


@router.get("", response_model=DocumentListDTO, summary="Listaa dokumentit")
async def list_documents(
    repository: DocumentRepository = Depends(get_document_repository),
) -> DocumentListDTO:
    """Palauttaa kaikki ladatut dokumentit (uusimmat ensin)."""
    documents = await repository.list()
    return DocumentListDTO(
        items=[DocumentDTO.from_entity(document) for document in documents],
        total=len(documents),
    )


@router.get("/{document_id}", response_model=DocumentDTO, summary="Hae dokumentti")
async def get_document(
    document_id: UUID,
    repository: DocumentRepository = Depends(get_document_repository),
) -> DocumentDTO:
    """Palauttaa yksittäisen dokumentin tiedot."""
    document = await repository.get(document_id)
    if document is None:
        raise NotFoundError(f"Dokumenttia {document_id} ei löydy")
    return DocumentDTO.from_entity(document)


@router.delete(
    "/{document_id}",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Poista dokumentti",
)
async def delete_document(
    document_id: UUID,
    repository: DocumentRepository = Depends(get_document_repository),
) -> None:
    """Poistaa dokumentin ja siihen liittyvät chunkit (kaskadi)."""
    document = await repository.get(document_id)
    if document is None:
        raise NotFoundError(f"Dokumenttia {document_id} ei löydy")
    await repository.delete(document_id)