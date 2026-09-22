# =============================================================================
# Infrastructure — PDF-palvelu (PyMuPDF)
# Toteuttaa PDFService-portin. Varsinainen purkulogiikka lisätään seuraavassa vaiheessa.
# =============================================================================
from __future__ import annotations

from app.core.logging import get_logger
from app.domain.interfaces.services import PDFService

logger = get_logger(__name__)


class PyMuPDFService(PDFService):
    """Purkaa PDF-tiedoston tekstiksi PyMuPDF-kirjastolla (fitz)."""

    async def extract_text(self, file_bytes: bytes) -> tuple[str, int]:
        """Palauttaa (koko teksti, sivumäärä). Toteutus lisätään seuraavassa vaiheessa."""
        raise NotImplementedError("Toteutetaan seuraavassa vaiheessa")