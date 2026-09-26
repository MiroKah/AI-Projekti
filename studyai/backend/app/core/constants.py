# =============================================================================
# Core — jaetut vakiot koko sovellukselle
# =============================================================================
from __future__ import annotations

# Tarkka vastaus, jota käytetään, kun ladatusta materiaalista ei löydy
# riittävästi tietoa kysymykseen. Sisältyy myös kielimallille annettuun
# promptiin (app.infrastructure.services.openai_service), joten lauseet
# täsmäävät aina.
NO_INFO_ANSWER = "Tähän kysymykseen ei löydy riittävästi tietoa ladatusta materiaalista."
