# =============================================================================
# Testit — PyMuPDFService (PDF-tekstin purku ja siivous)
# =============================================================================
from __future__ import annotations

from unittest.mock import MagicMock, patch

import fitz
import pytest
from app.core.exceptions import FileProcessingError
from app.infrastructure.services.pdf_service import PyMuPDFService

# -----------------------------------------------------------------------------
# Apufunktiot: rakentavat PDF-tavuvirtoja testejä varten (ei kiinteitä
# binääritiedostoja repositoriossa -> testit ovat itsenäisiä ja nopeita)
# -----------------------------------------------------------------------------


def _build_pdf_with_pages(texts: list[str]) -> bytes:
    """Rakentaa PDF:n, jossa on yksi sivu per annettu tekstipätkä."""
    document = fitz.open()
    try:
        for text in texts:
            page = document.new_page()
            if text:
                page.insert_text((72, 72), text)
        return document.tobytes()
    finally:
        document.close()


def _build_zero_page_document_double() -> MagicMock:
    """Rakentaa mock-fitz.Document:in, jossa page_count == 0.

    HUOM: PyMuPDF ei salli oikean 0-sivuisen PDF-tiedoston serialisointia
    (``ValueError: cannot save with zero pages``), joten tyhjän dokumentin
    tapaus simuloidaan mockilla ``fitz.open``-kutsun tasolla.
    """
    mock_document = MagicMock()
    mock_document.page_count = 0
    mock_document.__iter__ = MagicMock(return_value=iter([]))
    return mock_document


# -----------------------------------------------------------------------------
# Fixturet
# -----------------------------------------------------------------------------


@pytest.fixture
def pdf_service() -> PyMuPDFService:
    """Palauttaa PyMuPDFService-instanssin oletusasetuksin (25 MB raja)."""
    return PyMuPDFService()


# -----------------------------------------------------------------------------
# Onnistuneet tapaukset
# -----------------------------------------------------------------------------


class TestExtractTextSuccess:
    """Testaa onnistuneen PDF-purun ja tekstin siivouksen."""

    async def test_returns_text_and_correct_page_count(
        self, pdf_service: PyMuPDFService
    ) -> None:
        """Palauttaa poimitun tekstin ja oikean sivumäärän."""
        pdf_bytes = _build_pdf_with_pages(["Hello world", "Second page"])

        text, page_count = await pdf_service.extract_text(pdf_bytes)

        assert page_count == 2
        assert "Hello world" in text
        assert "Second page" in text

    async def test_single_page_document(self, pdf_service: PyMuPDFService) -> None:
        """Yhden sivun dokumentti palauttaa page_count == 1."""
        pdf_bytes = _build_pdf_with_pages(["Only page"])

        text, page_count = await pdf_service.extract_text(pdf_bytes)

        assert page_count == 1
        assert "Only page" in text

    async def test_result_has_no_leading_or_trailing_whitespace(
        self, pdf_service: PyMuPDFService
    ) -> None:
        """Palautettu teksti on siivottu (ei alku-/loppuvälilyöntejä)."""
        pdf_bytes = _build_pdf_with_pages(["Some content"])

        text, _ = await pdf_service.extract_text(pdf_bytes)

        assert text == text.strip()


class TestCleanText:
    """Testaa tekstin siivouslogiikkaa suoraan (rivinvaihdot, välilyönnit)."""

    def test_collapses_multiple_spaces_and_tabs(self) -> None:
        """Peräkkäiset välilyönnit/sarkaimet tiivistyvät yhdeksi välilyönniksi."""
        raw = "Sana1     Sana2\tSana3"

        cleaned = PyMuPDFService._clean_text(raw)

        assert cleaned == "Sana1 Sana2 Sana3"

    def test_strips_trailing_whitespace_on_each_line(self) -> None:
        """Rivien alku- ja loppuvälilyönnit poistuvat."""
        raw = "  Rivi yksi   \n   Rivi kaksi  "

        cleaned = PyMuPDFService._clean_text(raw)

        assert cleaned == "Rivi yksi\nRivi kaksi"

    def test_collapses_excessive_blank_lines_to_paragraph_break(self) -> None:
        """Kolme+ peräkkäistä rivinvaihtoa tiivistyy kahdeksi (kappaleväli)."""
        raw = "Kappale yksi\n\n\n\n\nKappale kaksi"

        cleaned = PyMuPDFService._clean_text(raw)

        assert cleaned == "Kappale yksi\n\nKappale kaksi"

    def test_normalizes_windows_and_mac_line_endings(self) -> None:
        """Windows (\\r\\n) ja vanha Mac (\\r) -rivinvaihdot normalisoituvat."""
        raw = "Rivi1\r\nRivi2\rRivi3"

        cleaned = PyMuPDFService._clean_text(raw)

        assert cleaned == "Rivi1\nRivi2\nRivi3"

    def test_empty_string_returns_empty_string(self) -> None:
        """Tyhjä syöte palauttaa tyhjän merkkijonon (ei virhettä)."""
        assert PyMuPDFService._clean_text("") == ""

    def test_whitespace_only_returns_empty_string(self) -> None:
        """Vain välilyönteistä/rivinvaihdoista koostuva syöte siivoutuu tyhjäksi."""
        assert PyMuPDFService._clean_text("   \n\n   \t  \n") == ""


# -----------------------------------------------------------------------------
# Virhetilanteet
# -----------------------------------------------------------------------------


class TestExtractTextErrors:
    """Testaa virheenkäsittelyä: korruptoitunut, tyhjä ja liian suuri PDF."""

    async def test_corrupted_pdf_raises_file_processing_error(
        self, pdf_service: PyMuPDFService
    ) -> None:
        """Ei-kelvollinen/vioittunut PDF-data nostaa FileProcessingError-poikkeuksen."""
        corrupted_bytes = b"Tama ei ole kelvollinen PDF-tiedosto ollenkaan"

        with pytest.raises(FileProcessingError, match="vioittunut"):
            await pdf_service.extract_text(corrupted_bytes)

    async def test_empty_bytes_raises_file_processing_error(
        self, pdf_service: PyMuPDFService
    ) -> None:
        """Täysin tyhjä tavuvirta (0 tavua) nostaa FileProcessingError-poikkeuksen."""
        with pytest.raises(FileProcessingError):
            await pdf_service.extract_text(b"")

    async def test_pdf_with_zero_pages_raises_file_processing_error(
        self, pdf_service: PyMuPDFService
    ) -> None:
        """PDF, jossa on 0 sivua, nostaa FileProcessingError-poikkeuksen."""
        zero_page_document = _build_zero_page_document_double()

        with (
            patch("app.infrastructure.services.pdf_service.fitz.open", return_value=zero_page_document),
            pytest.raises(FileProcessingError, match="tyhjä"),
        ):
            await pdf_service.extract_text(b"%PDF-1.4 irrelevant-bytes-because-fitz.open-is-mocked")

    async def test_pdf_without_extractable_text_raises_file_processing_error(
        self, pdf_service: PyMuPDFService
    ) -> None:
        """PDF, jonka sivuilla ei ole tulkittavaa tekstiä, nostaa virheen."""
        blank_page_pdf_bytes = _build_pdf_with_pages([""])

        with pytest.raises(FileProcessingError, match="ei sisällä tulkittavaa tekstiä"):
            await pdf_service.extract_text(blank_page_pdf_bytes)

    async def test_file_exceeding_max_size_raises_file_processing_error(self) -> None:
        """Tiedosto, joka ylittää sallitun enimmäiskoon, nostaa virheen."""
        pdf_bytes = _build_pdf_with_pages(["Riittävän pieni sisältö"])
        # Asetetaan raja pienemmäksi kuin testi-PDF:n koko -> raja ylittyy varmasti
        service = PyMuPDFService(max_size_bytes=1)

        with pytest.raises(FileProcessingError, match="liian suuri"):
            await service.extract_text(pdf_bytes)

    async def test_max_size_boundary_is_inclusive(self) -> None:
        """Tiedosto, joka on tarkalleen rajan kokoinen, EI nosta virhettä koon takia."""
        pdf_bytes = _build_pdf_with_pages(["Raja-arvon testaus"])
        service = PyMuPDFService(max_size_bytes=len(pdf_bytes))

        text, page_count = await service.extract_text(pdf_bytes)

        assert page_count == 1
        assert "Raja-arvon testaus" in text
