# =============================================================================
# Core — logging-konfiguraatio
# Yhtenäinen lokitus koko sovellukselle.
# =============================================================================
from __future__ import annotations

import logging
import sys

from app.core.config import settings

# Lokituksen muoto
_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def configure_logging() -> None:
    """Konfiguroi juurilokittajan sovelluksen asetusten mukaisesti."""
    level = logging.DEBUG if settings.DEBUG else logging.INFO

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(fmt=_LOG_FORMAT, datefmt=_DATE_FORMAT))

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)

    # Vähennetään kohinaa kolmannen osapuolen kirjastoista
    for noisy in ("uvicorn.access", "httpx", "openai", "httpcore"):
        logging.getLogger(noisy).setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Palauttaa nimellä varustetun lokittajan."""
    return logging.getLogger(name)