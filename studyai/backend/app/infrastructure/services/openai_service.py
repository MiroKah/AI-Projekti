# =============================================================================
# Infrastructure — OpenAI-palvelutoteutukset
# Toteuttaa EmbeddingService- ja LLMService-portit OpenAI:n API:a vasten.
# =============================================================================
from __future__ import annotations

from collections.abc import Sequence

from openai import APIError, APITimeoutError, AsyncOpenAI, RateLimitError
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.core.config import settings
from app.core.constants import NO_INFO_ANSWER
from app.core.exceptions import AIProviderError
from app.core.logging import get_logger
from app.domain.interfaces.services import EmbeddingService, LLMService

logger = get_logger(__name__)

# Uudelleenyrityskelpoiset OpenAI-virheet (väliaikaiset: rate limit, timeout, 5xx)
_RETRYABLE_ERRORS = (RateLimitError, APITimeoutError, APIError)

# OpenAI Embeddings API:n suurin sallittu erän koko yhdessä pyynnössä
_EMBEDDING_BATCH_SIZE = 100

# Vastaukset pidetään mahdollisimman toistettavina (grounded) → matala temperature
_CHAT_TEMPERATURE = 0.2

# Järjestelmäprompti: vastaus perustuu VAIN annettuun materiaaliin. Tarkka
# "ei tietoa" -lause on jaettu vakio (app.core.constants), jotta use case ja
# prompt täsmäävät aina.
_SYSTEM_PROMPT = (
    "Olet StudyAI-oppimisavustaja. "
    "Vastaa käyttäjän kysymykseen VAIN alla annetun materiaalin perusteella. "
    "Älä käytä aiempaa tietoa tai yleistä osaamistasi, äläkä keksi tietoa. "
    'Jos vastausta ei löydy materiaalista, vastaa tarkalleen lauseella: '
    f'"{NO_INFO_ANSWER}"'
)


def _build_user_prompt(*, question: str, context: str) -> str:
    """Kootaan konteksti (lähteet) ja kysymys yhdeksi käyttäjän viestiksi."""
    return f"Materiaali (ladattu dokumentti):\n\n{context}\n\nKysymys: {question}"


class OpenAIEmbeddingService(EmbeddingService):
    """Luo tekstin upotukset OpenAI Embeddings -rajapinnalla (text-embedding-3-small)."""

    def __init__(self, client: AsyncOpenAI | None = None) -> None:
        self._client = client or AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self._model = settings.OPENAI_EMBEDDING_MODEL
        self._dimensions = settings.OPENAI_EMBEDDING_DIMENSIONS

    async def embed_text(self, text: str) -> list[float]:
        """Luo embedding yhdelle tekstille."""
        vectors = await self.embed_batch([text])
        return vectors[0]

    async def embed_batch(self, texts: Sequence[str]) -> list[list[float]]:
        """Luo embeddingit usealle tekstille kerralla (erotellaan API-rajan mukaan)."""
        if not texts:
            return []

        all_vectors: list[list[float]] = []
        for start in range(0, len(texts), _EMBEDDING_BATCH_SIZE):
            batch = list(texts[start : start + _EMBEDDING_BATCH_SIZE])
            try:
                all_vectors.extend(await self._embed_batch_with_retry(batch))
            except _RETRYABLE_ERRORS as exc:
                # Uudelleenyritykset on käytetty loppuun → yhtenäinen virhe
                logger.exception("OpenAI embeddings -kutsu epäonnistui uudelleenyritysten jälkeen")
                raise AIProviderError("Embeddingin luonti epäonnistui") from exc
        return all_vectors

    @retry(
        retry=retry_if_exception_type(_RETRYABLE_ERRORS),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        stop=stop_after_attempt(3),
        reraise=True,
    )
    async def _embed_batch_with_retry(self, batch: list[str]) -> list[list[float]]:
        """Kutsuu OpenAI Embeddings API:a uudelleenyrityksin väliaikaisille virheille."""
        try:
            response = await self._client.embeddings.create(
                model=self._model,
                input=batch,
                dimensions=self._dimensions,
            )
        except _RETRYABLE_ERRORS:
            raise
        except Exception as exc:
            logger.exception("OpenAI embeddings -kutsu epäonnistui")
            raise AIProviderError("Embeddingin luonti epäonnistui") from exc

        # OpenAI palauttaa tulokset samassa järjestyksessä kuin input-lista
        return [item.embedding for item in response.data]


class OpenAILLMService(LLMService):
    """Generoi vastauksia OpenAI Chat Completions -rajapinnalla (gpt-4o-mini).

    HUOM: asennettu openai-kirjasto (1.59.6) ei vielä sisällä Responses APIa,
    joten käytetään chat.completions.create-kutsua.
    """

    def __init__(self, client: AsyncOpenAI | None = None) -> None:
        self._client = client or AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self._model = settings.OPENAI_CHAT_MODEL

    async def generate_answer(self, *, question: str, context: str) -> str:
        """Generoi vastauksen annetun kontekstin perusteella (vain materiaali)."""
        try:
            return await self._create_completion(
                system_prompt=_SYSTEM_PROMPT,
                user_prompt=_build_user_prompt(question=question, context=context),
            )
        except _RETRYABLE_ERRORS as exc:
            # Uudelleenyritykset on käytetty loppuun → yhtenäinen virhe kodiksi
            logger.exception("OpenAI chat -kutsu epäonnistui uudelleenyritysten jälkeen")
            raise AIProviderError("Vastauksen generointi epäonnistui") from exc

    @retry(
        retry=retry_if_exception_type(_RETRYABLE_ERRORS),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        stop=stop_after_attempt(3),
        reraise=True,
    )
    async def _create_completion(self, *, system_prompt: str, user_prompt: str) -> str:
        """Kutsuu OpenAI Chat Completions APIa uudelleenyrityksin väliaikaisille virheille."""
        try:
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=_CHAT_TEMPERATURE,
            )
        except _RETRYABLE_ERRORS:
            raise
        except Exception as exc:
            logger.exception("OpenAI chat -kutsu epäonnistui")
            raise AIProviderError("Vastauksen generointi epäonnistui") from exc

        content = response.choices[0].message.content if response.choices else None
        if not content:
            raise AIProviderError("OpenAI palautti tyhjän vastauksen")
        return content.strip()