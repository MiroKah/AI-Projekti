# =============================================================================
# Presentation — dokumentin indeksointireitti (RAG-putki)
# Vastaanottaa PDF:n, purkaa tekstin, pilkkoo, luo embeddingit OpenAI:lla
# (text-embedding-3-small) ja tallentaa chunkit + vektorit pgvectoriin.
# =============================================================================
from __future__ import annotations

from fastapi import APIRouter, Depends, File, UploadFile, status

from app.application.dtos.document_dto import DocumentDTO, UploadResultDTO
from app.application.use_cases.upload_document import UploadDocumentUseCase
from app.presentation.api.v1.routes._pdf_upload import read_pdf_bytes
from app.presentation.dependencies import get_upload_document_use_case

router = APIRouter()


@router.post(
    "/index-document",
    response_model=UploadResultDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Indeksoi PDF-dokumentti (RAG): tekstin purku, chunkkaus, embeddingit, tallennus",
)
async def index_document(
    file: UploadFile = File(..., description="Indeksoitava PDF-tiedosto"),
    use_case: UploadDocumentUseCase = Depends(get_upload_document_use_case),
) -> UploadResultDTO:
    """Indeksoi PDF-dokumentin koko RAG-putken läpi.

    Prosessi:
      1. Lue PDF:n teksti (PyMuPDF)
      2. Pilko teksti (chunk_size=1000, chunk_overlap=200)
      3. Luo embeddingit OpenAI:lla (text-embedding-3-small)
      4. Tallenna document + chunk + embedding PostgreSQL/pgvectoriin

    Palauttaa luodun dokumentin, chunkkien määrän ja tilaviestin.
    """
    file_bytes = await read_pdf_bytes(file)

    result = await use_case.execute(
        filename=file.filename or "document.pdf",
        file_bytes=file_bytes,
    )

    return UploadResultDTO(
        document=DocumentDTO.from_entity(result.document),
        chunks_created=result.chunks_created,
        message=f"Dokumentti indeksoitu onnistuneesti ({result.chunks_created} chunkkia)",
    )
