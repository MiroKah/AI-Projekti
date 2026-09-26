# =============================================================================
# Presentation — jaettu PDF-latauksen validointi reiteille
# Tarkistaa tiedostotyypin ja koon, lukee tiedoston tavut.
# =============================================================================
from __future__ import annotations

from fastapi import UploadFile

from app.core.config import settings
from app.core.exceptions import ValidationError

# Sallitut PDF-tiedostotyypit (MIME + tiedostopääte varmuuden vuoksi)
_ALLOWED_CONTENT_TYPES = {"application/pdf"}
_ALLOWED_EXTENSION = ".pdf"


async def read_pdf_bytes(file: UploadFile) -> bytes:
    """Validoi PDF-latauksen (tyyppi + koko) ja palauttaa tiedoston tavut.

    Raises:
        ValidationError: ei-PDF tai tiedosto ylittää enimmäiskoon.
    """
    filename = file.filename or ""
    has_pdf_extension = filename.lower().endswith(_ALLOWED_EXTENSION)
    has_pdf_content_type = file.content_type in _ALLOWED_CONTENT_TYPES
    if not (has_pdf_extension or has_pdf_content_type):
        raise ValidationError("Vain PDF-tiedostot ovat sallittuja (.pdf)")

    file_bytes = await file.read()
    if len(file_bytes) > settings.max_upload_size_bytes:
        max_mb = settings.MAX_UPLOAD_SIZE_MB
        raise ValidationError(f"Tiedosto on liian suuri (enimmäiskoko {max_mb} MB)")
    return file_bytes
