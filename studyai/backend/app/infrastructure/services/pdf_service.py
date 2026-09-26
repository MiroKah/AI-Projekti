# =============================================================================
# Infrastructure — PDF-palvelu (PyMuPDF / fitz)
# Toteuttaa domain-portin PDFService: lukee PDF:n, poimii tekstin ja siivoaa sen.
# =============================================================================
from __future__ import annotations

import asyncio
import re

import fitz

from app.core.config import settings
from app.core.exceptions import FileProcessingError
from app.core.logging import get_logger
from app.domain.interfaces.services import PDFService

logger = get_logger(__name__)


class PyMuPDFService(PDFService):
    """Purkaa PDF-tiedoston tekstiksi PyMuPDF-kirjastolla (fitz).

    Vastuut:
      - Lukee PDF-tiedoston tavuina ja avaa sen fitz-dokumentiksi
      - Hakee dokumentin sivumäärän
      - Poimii kaikkien sivujen tekstin
      - Siivoaa rivinvaihdot ja ylimääräiset välilyönnit
      - Palauttaa yhtenäisen, siistin tekstin

    Virheenkäsittely (kaikki nostetaan ``FileProcessingError``-poikkeuksena):
      - liian suuri tiedosto (ylittää ``MAX_UPLOAD_SIZE_MB``)
      - vioittunut / ei-kelvollinen PDF-tiedosto
      - tyhjä PDF (0 sivua)
      - PDF, joka ei sisällä tulkittavaa tekstiä (esim. skannattu kuva)
    """

    # Peräkkäiset välilyönnit/sarkaimet tiivistetään yhdeksi välilyönniksi
    _WHITESPACE_RE = re.compile(r"[ \t\f\v]+")
    # Kolme tai useampi peräkkäistä rivinvaihtoa tiivistetään kahdeksi (kappaleväli)
    _MULTI_NEWLINE_RE = re.compile(r"\n{3,}")

    def __init__(self, max_size_bytes: int | None = None) -> None:
        """
        Args:
            max_size_bytes: Sallittu enimmäistiedostokoko tavuina.
                Oletuksena ``settings.MAX_UPLOAD_SIZE_MB``.
        """
        self._max_size_bytes = (
            max_size_bytes if max_size_bytes is not None else settings.max_upload_size_bytes
        )

    async def extract_text(self, file_bytes: bytes) -> tuple[str, int]:
        """Purkaa PDF:n tekstiksi. Palauttaa (siivottu teksti, sivumäärä).

        Raises:
            FileProcessingError: tiedosto on liian suuri, vioittunut, tyhjä
                tai ei sisällä tulkittavaa tekstiä.
        """
        self._validate_size(file_bytes)
        # PyMuPDF on synkroninen/CPU-sidonnainen kirjasto -> ajetaan erillisessä
        # threadissa, jotta se ei jumita asyncio-tapahtumasilmukkaa.
        return await asyncio.to_thread(self._extract_text_sync, file_bytes)

    # -------------------------------------------------------------------------
    # Sisäinen, synkroninen toteutus
    # -------------------------------------------------------------------------

    def _extract_text_sync(self, file_bytes: bytes) -> tuple[str, int]:
        """Suorittaa varsinaisen PDF-purun synkronisesti."""
        document = self._open_document(file_bytes)
        try:
            page_count = document.page_count
            self._validate_not_empty(page_count)
            raw_text = self._extract_raw_text(document)
        finally:
            document.close()

        cleaned_text = self._clean_text(raw_text)
        if not cleaned_text:
            logger.warning("PDF avattu (%s sivua), mutta tekstiä ei löytynyt", page_count)
            raise FileProcessingError("PDF-tiedosto ei sisällä tulkittavaa tekstiä")

        logger.info(
            "PDF purettu onnistuneesti: %s sivua, %s merkkiä", page_count, len(cleaned_text)
        )
        return cleaned_text, page_count

    def _validate_size(self, file_bytes: bytes) -> None:
        """Varmista, ettei tiedosto ylitä sallittua enimmäiskokoa."""
        if len(file_bytes) > self._max_size_bytes:
            max_mb = self._max_size_bytes / (1024 * 1024)
            raise FileProcessingError(
                f"PDF-tiedosto on liian suuri (enimmäiskoko {max_mb:.0f} MB)"
            )

    @staticmethod
    def _open_document(file_bytes: bytes) -> fitz.Document:
        """Avaa PDF-tavuvirran fitz-dokumentiksi.

        Raises:
            FileProcessingError: data ei ole kelvollinen/avattava PDF.
        """
        try:
            return fitz.open(stream=file_bytes, filetype="pdf")
        except Exception as exc:  # PyMuPDF nostaa esim. FileDataError/RuntimeError
            raise FileProcessingError(
                "PDF-tiedosto on vioittunut tai sitä ei voitu avata"
            ) from exc

    @staticmethod
    def _validate_not_empty(page_count: int) -> None:
        """Varmista, että dokumentissa on vähintään yksi sivu."""
        if page_count == 0:
            raise FileProcessingError("PDF-tiedosto on tyhjä (0 sivua)")

    @staticmethod
    def _extract_raw_text(document: fitz.Document) -> str:
        """Poimii kaikkien sivujen tekstin ja yhdistää ne kappalein erotettuina."""
        pages_text = [page.get_text() for page in document]
        return "\n\n".join(pages_text)

    @classmethod
    def _clean_text(cls, text: str) -> str:
        """Siivoaa rivinvaihdot ja ylimääräiset välilyönnit, palauttaa yhtenäisen tekstin."""
        # Normalisoi rivinvaihdot (Windows \r\n ja vanha Mac \r -> Unix \n)
        normalized = text.replace("\r\n", "\n").replace("\r", "\n")
        # Poista rivien alku- ja loppuvälilyönnit
        lines = [line.strip() for line in normalized.split("\n")]
        joined = "\n".join(lines)
        # Tiivistä peräkkäiset välilyönnit/sarkaimet yhdeksi välilyönniksi
        collapsed_spaces = cls._WHITESPACE_RE.sub(" ", joined)
        # Tiivistä 3+ peräkkäistä rivinvaihtoa kahdeksi (säilytä kappalejako)
        collapsed_newlines = cls._MULTI_NEWLINE_RE.sub("\n\n", collapsed_spaces)
        return collapsed_newlines.strip()