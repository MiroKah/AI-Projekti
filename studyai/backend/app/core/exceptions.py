# =============================================================================
# Core — sovelluskohtaiset poikkeukset
# Yhtenäinen virheenkäsittely koko sovellukselle.
# =============================================================================
from __future__ import annotations


class StudyAIError(Exception):
    """Kaikkien sovelluspoikkeusten perusluokka."""

    def __init__(self, message: str, *, status_code: int = 500) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class NotFoundError(StudyAIError):
    """Pyydettyä resurssia ei löytynyt."""

    def __init__(self, message: str = "Resurssia ei löytynyt") -> None:
        super().__init__(message, status_code=404)


class ValidationError(StudyAIError):
    """Syötteen validointi epäonnistui."""

    def __init__(self, message: str = "Virheellinen syöte") -> None:
        super().__init__(message, status_code=422)


class FileProcessingError(StudyAIError):
    """Tiedoston käsittely (esim. PDF-purku) epäonnistui."""

    def __init__(self, message: str = "Tiedoston käsittely epäonnistui") -> None:
        super().__init__(message, status_code=400)


class AIProviderError(StudyAIError):
    """AI-palveluntarjoajan (OpenAI) kutsu epäonnistui."""

    def __init__(self, message: str = "AI-palvelun kutsu epäonnistui") -> None:
        super().__init__(message, status_code=502)


class DatabaseError(StudyAIError):
    """Tietokantaoperaatio epäonnistui."""

    def __init__(self, message: str = "Tietokantavirhe") -> None:
        super().__init__(message, status_code=500)