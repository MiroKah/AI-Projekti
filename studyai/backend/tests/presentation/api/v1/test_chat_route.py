# =============================================================================
# Testit — POST /api/chat -reitti (reitin sopimus + poikkeukset)
# Käyttää FastAPI:n dependency overridea: ei tietokantaa eikä OpenAIia.
# =============================================================================
from __future__ import annotations

from uuid import UUID, uuid4

from app.application.use_cases.chat_with_document import ChatResult
from app.core.exceptions import NotFoundError
from app.domain.entities.chat import ChatMessage, ChatRole, ChatSession, SourceReference
from app.presentation.api.v1.router import api_router
from app.presentation.dependencies import get_chat_with_document_use_case
from app.presentation.middleware import register_exception_handlers
from fastapi import FastAPI
from fastapi.testclient import TestClient


class FakeChatUseCase:
    """Selkeä feikki use caselle: palauttaa valmiin tuloksen tai heittää virheen."""

    def __init__(self, *, error: Exception | None = None) -> None:
        self.error = error
        self.calls: list[dict] = []

    async def execute(
        self, *, question: str, document_id: UUID, session_id: UUID | None = None
    ) -> ChatResult:
        self.calls.append(
            {"question": question, "document_id": document_id, "session_id": session_id}
        )
        if self.error is not None:
            raise self.error

        session = ChatSession(id=uuid4(), document_id=document_id, title=question[:50])
        message = ChatMessage(
            id=uuid4(),
            session_id=session.id,
            role=ChatRole.ASSISTANT,
            content="Vastaus materiaalista.",
            sources=[
                SourceReference(
                    chunk_id=uuid4(),
                    document_id=document_id,
                    chunk_index=2,
                    snippet="Ote materiaalista",
                    score=0.87,
                )
            ],
        )
        return ChatResult(session=session, message=message)


def _make_client(use_case: FakeChatUseCase) -> TestClient:
    """Rakentaa testattavan sovelluksen (reitit + poikkeuskäsittelijät + DI-override)."""
    app = FastAPI(title="test")
    app.include_router(api_router, prefix="/api")
    register_exception_handlers(app)
    app.dependency_overrides[get_chat_with_document_use_case] = lambda: use_case
    return TestClient(app)


def test_chat_returns_json_with_session_message_and_sources() -> None:
    use_case = FakeChatUseCase()
    client = _make_client(use_case)
    document_id = str(uuid4())

    response = client.post(
        "/api/chat",
        json={"document_id": document_id, "question": "Mitä dokumentissa on?"},
    )

    assert response.status_code == 200
    body = response.json()

    # Pyynnön tiedot välittyivät use caseen (UUID muunnettu takaisin)
    assert use_case.calls[0]["question"] == "Mitä dokumentissa on?"
    assert str(use_case.calls[0]["document_id"]) == document_id
    assert use_case.calls[0]["session_id"] is None

    # JSON-vastaus: session_id + viesti lähteineen
    message = body["message"]
    assert body["session_id"] == message["session_id"]
    assert message["role"] == "assistant"
    assert message["content"] == "Vastaus materiaalista."
    assert len(message["sources"]) == 1

    source = message["sources"][0]
    assert source["document_id"] == document_id
    assert source["chunk_index"] == 2
    assert source["snippet"] == "Ote materiaalista"
    assert source["score"] == 0.87


def test_missing_document_id_returns_422() -> None:
    client = _make_client(FakeChatUseCase())

    response = client.post("/api/chat", json={"question": "Kysymys"})

    assert response.status_code == 422


def test_null_document_id_returns_422() -> None:
    client = _make_client(FakeChatUseCase())

    response = client.post("/api/chat", json={"document_id": None, "question": "Kysymys"})

    assert response.status_code == 422


def test_missing_question_returns_422() -> None:
    client = _make_client(FakeChatUseCase())

    response = client.post("/api/chat", json={"document_id": str(uuid4())})

    assert response.status_code == 422


def test_not_found_from_use_case_is_mapped_to_404() -> None:
    client = _make_client(FakeChatUseCase(error=NotFoundError("Dokumenttia ei löydy")))

    response = client.post(
        "/api/chat",
        json={"document_id": str(uuid4()), "question": "Kysymys"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Dokumenttia ei löydy"
