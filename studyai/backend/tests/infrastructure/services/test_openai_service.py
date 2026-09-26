# =============================================================================
# Testit — OpenAILLMService (prompt, virheenkäsittely, uudelleenyritykset)
# =============================================================================
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock

import httpx
import pytest
from app.core.config import settings
from app.core.constants import NO_INFO_ANSWER
from app.core.exceptions import AIProviderError
from app.infrastructure.services.openai_service import OpenAILLMService
from openai import RateLimitError


def _completion_response(content: str | None) -> SimpleNamespace:
    """Rakentaa OpenAI Chat Completions -vastauksen rakenteen (mock)."""
    return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=content))])


def _make_client(
    *, content: str | None = "Vastaus materiaalista.", error: Exception | None = None
) -> tuple[SimpleNamespace, AsyncMock]:
    """Luo feikin AsyncOpenAI-klientin, joka palauttaa vastauksen tai virheen."""
    create = AsyncMock()
    if error is not None:
        create.side_effect = error
    else:
        create.return_value = _completion_response(content)
    client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))
    return client, create


def _rate_limit_error() -> RateLimitError:
    """Rakentaa openai.RateLimitError-virheen (vaatii httpx-responsen)."""
    request = httpx.Request("POST", "https://api.openai.com/v1/chat/completions")
    response = httpx.Response(status_code=429, request=request)
    return RateLimitError("Rate limit exceeded", response=response, body=None)


class TestGenerateAnswer:
    """generate_answer: prompt, mallin valinta ja vastauksen muoto."""

    async def test_prompt_uses_only_material_and_exact_fallback_sentence(self) -> None:
        client, create = _make_client(content="  Perusteltu vastaus.  ")
        service = OpenAILLMService(client=client)

        answer = await service.generate_answer(
            question="Mitä sivulla 3 lukee?",
            context="[Lähde 1] (chunk #0, samankaltaisuus 0.900)\nSivun kolme sisältö.",
        )

        assert answer == "Perusteltu vastaus."
        create.assert_awaited_once()

        kwargs = create.await_args.kwargs
        assert kwargs["model"] == settings.OPENAI_CHAT_MODEL
        assert kwargs["temperature"] == 0.2
        assert kwargs["messages"][0]["role"] == "system"
        assert kwargs["messages"][1]["role"] == "user"

        system_prompt = kwargs["messages"][0]["content"]
        user_prompt = kwargs["messages"][1]["content"]
        # Vastaus rajataan materiaaliin + tarkka "ei tietoa" -lause promptissa
        assert "VAIN" in system_prompt
        assert NO_INFO_ANSWER in system_prompt
        # Kysymys ja konteksti käyttäjän viestissä
        assert "Mitä sivulla 3 lukee?" in user_prompt
        assert "Sivun kolme sisältö." in user_prompt

    async def test_empty_answer_raises_ai_provider_error(self) -> None:
        client, _ = _make_client(content="")
        service = OpenAILLMService(client=client)

        with pytest.raises(AIProviderError):
            await service.generate_answer(question="Kysymys?", context="Konteksti")

    async def test_unexpected_error_is_wrapped_as_ai_provider_error(self) -> None:
        client, create = _make_client(error=ValueError("boom"))
        service = OpenAILLMService(client=client)

        with pytest.raises(AIProviderError):
            await service.generate_answer(question="Kysymys?", context="Konteksti")

        # Ei uudelleenyrityksiä ei-kelpoavalle virheelle
        assert create.await_count == 1

    async def test_rate_limit_is_retried_then_converted_after_exhaustion(self) -> None:
        client, create = _make_client(error=_rate_limit_error())
        service = OpenAILLMService(client=client)

        with pytest.raises(AIProviderError):
            await service.generate_answer(question="Kysymys?", context="Konteksti")

        # Kolme yritystä (retry) ja lopuksi yhtenäinen AIProviderError
        assert create.await_count == 3
