# =============================================================================
# Infrastructure — SQLAlchemy deklaratiivinen perusta
# Kaikki ORM-mallit perivät tämän (Base.metadata käytössä Alembicissa).
# =============================================================================
from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Deklaratiivinen perusluokka kaikille ORM-malleille."""