# =============================================================================
# Testit — ChatWithDocumentUseCase (RAG-kysely, fake-riippuvuudet)
# =============================================================================
from __future__ import annotations

from collections.abc import Sequence
from uuid import UUID, uuid4

import pytest
from app.application.use_cases.chat_with_document import ChatWithDocumentUseCase
from app.core.constants import NO_INFO_ANSWER
from app.core.exceptions import NotFoundError, ValidationError
from app.domain.entities.chat import ChatMessage, ChatRole, ChatSession
from app.domain.entities.chunk import Chunk
from app.domain.entities.document import Document


class FakeDocumentRepository:
    """Muistinvarainen DocumentRepository-fake testejä varten."""

    def __init__(self, documents: Sequence[Document] = ()) -> None:
        self.documents: dict[UUID, Document] = {d.id: d for d in documents}

    async def add(self, document: Document) -> Document:
        self.documents[document.id] = document
        return document

    async def get(self, document_id: UUID) -> Document | None:
        return self.documents.get(document_id)

    async def list(self) -> Sequence[Document]:
        return list(self.documents.values())

    async def update(self, document: Document) -> Document:
        self.documents[document.id] = document
        return document

    async def delete(self, document_id: UUID) -> None:
        self.documents.pop(document_id, None)


class FakeChunkRepository:
    """Palauttaa ennalta määrätyt hakutulokset ja kirjaa kutsuparametrit."""

    def __init__(self, results: Sequence[tuple[Chunk, float]] = ()) -> None:
        self.results = list(results)
        self.search_calls: list[dict] = []

    async def add_many(self, chunks: Sequence[Chunk]) -> None:
        self.results.extend((c, 1.0) for c in chunks)

    async def delete_by_document(self, document_id: UUID) -> None:
        self.results = [(c, s) for c, s in self.results if c.document_id != document_id]

    async def similarity_search(
        self, query_embedding: list[float], *, document_id: UUID | None = None, top_k: int = 5
    ) -> Sequence[tuple[Chunk, float]]:
        self.search_calls.append(
            {
                "query_embedding": query_embedding,
                "document_id": document_id,
                "top_k": top_k,
            }
        )
        return self.results


class FakeChatRepository:
    """Muistinvarainen ChatRepository-fake testejä varten."""

    def __init__(self, sessions: Sequence[ChatSession] = ()) -> None:
        self.sessions: dict[UUID, ChatSession] = {s.id: s for s in sessions}
        self.created_sessions: list[ChatSession] = []
        self.messages: list[ChatMessage] = []

    async def create_session(self, session: ChatSession) -> ChatSession:
        self.sessions[session.id] = session
        self.created_sessions.append(session)
        return session

    async def get_session(self, session_id: UUID) -> ChatSession | None:
        return self.sessions.get(session_id)

    async def add_message(self, message: ChatMessage) -> ChatMessage:
        self.messages.append(message)
        return message

    async def list_messages(self, session_id: UUID) -> Sequence[ChatMessage]:
        return [m for m in self.messages if m.session_id == session_id]


class FakeEmbeddingService:
    """Palauttaa ennalta määrätyn vektorin kysymykselle ja kirjaa tekstin."""

    def __init__(self) -> None:
        self.texts: list[str] = []

    async def embed_text(self, text: str) -> list[float]:
        self.texts.append(text)
        return [0.25, 0.75]

    async def embed_batch(self, texts: Sequence[str]) -> list[list[float]]:
        return [[0.5] for _ in texts]


class FakeLLMService:
    """Palauttaa ennalta määrätyt vastauksen ja kirjaa kutsut."""

    def __init__(self, answer: str = "Generoitu vastaus materiaalista.") -> None:
        self.answer = answer
        self.calls: list[dict] = []

    async def generate_answer(self, *, question: str, context: str) -> str:
        self.calls.append({"question": question, "context": context})
        return self.answer


def _make_document(document_id: UUID | None = None) -> Document:
    """Luo testidokumentin (ei tallenneta mihinkään)."""
    return Document(id=document_id or uuid4(), filename="doc.pdf", title="Doc")


def _make_chunk(document_id: UUID, index: int = 0, content: str = "Sisältö") -> Chunk:
    """Luo testichunkin dokumentille."""
    return Chunk(id=uuid4(), document_id=document_id, chunk_index=index, content=content)


def _prepare(
    *,
    document_repository: FakeDocumentRepository,
    chat_repository: FakeChatRepository,
    embedding_service: FakeEmbeddingService,
    llm_service: FakeLLMService,
    results: Sequence[tuple[Chunk, float]] = (),
    top_k: int = 5,
) -> tuple[ChatWithDocumentUseCase, FakeChunkRepository]:
    """Luo fake-chunkrepositoryn ja use casen (palauttaa molemmat vertailuun)."""
    chunk_repository = FakeChunkRepository(results)
    use_case = ChatWithDocumentUseCase(
        document_repository=document_repository,
        chunk_repository=chunk_repository,
        chat_repository=chat_repository,
        embedding_service=embedding_service,
        llm_service=llm_service,
        retrieval_top_k=top_k,
    )
    return use_case, chunk_repository


@pytest.fixture
def document() -> Document:
    return _make_document()


@pytest.fixture
def document_repository(document: Document) -> FakeDocumentRepository:
    return FakeDocumentRepository([document])


@pytest.fixture
def chat_repository() -> FakeChatRepository:
    return FakeChatRepository()


@pytest.fixture
def embedding_service() -> FakeEmbeddingService:
    return FakeEmbeddingService()


@pytest.fixture
def llm_service() -> FakeLLMService:
    return FakeLLMService()


class TestChatUseCaseHappyPath:
    """Onnistunut RAG-kysely: embedding, haku, LLM-vastaus, lähteet ja tallennus."""

    async def test_returns_assistant_message_with_sources(
        self, document, document_repository, chat_repository, embedding_service, llm_service
    ) -> None:
        chunk1 = _make_chunk(document.id, index=0, content="Ensimmäinen palanen")
        chunk2 = _make_chunk(document.id, index=1, content="Toinen palanen")
        use_case, _ = _prepare(
            document_repository=document_repository,
            chat_repository=chat_repository,
            embedding_service=embedding_service,
            llm_service=llm_service,
            results=[(chunk1, 0.91), (chunk2, 0.72)],
        )

        result = await use_case.execute(
            question="Mitä dokumentissa sanotaan?", document_id=document.id
        )

        assert result.message.role is ChatRole.ASSISTANT
        assert result.message.content == llm_service.answer
        assert result.message.session_id == result.session.id

        assert len(result.message.sources) == 2
        source = result.message.sources[0]
        assert source.chunk_id == chunk1.id
        assert source.document_id == document.id
        assert source.chunk_index == 0
        assert source.snippet == "Ensimmäinen palanen"
        assert source.score == 0.91

    async def test_saves_user_and_assistant_messages_in_order(
        self, document, document_repository, chat_repository, embedding_service, llm_service
    ) -> None:
        chunk = _make_chunk(document.id, content="Materiaalin sisältö")
        use_case, _ = _prepare(
            document_repository=document_repository,
            chat_repository=chat_repository,
            embedding_service=embedding_service,
            llm_service=llm_service,
            results=[(chunk, 0.8)],
        )

        await use_case.execute(question="Kysymys", document_id=document.id)

        assert [m.role for m in chat_repository.messages] == [
            ChatRole.USER,
            ChatRole.ASSISTANT,
        ]
        assert chat_repository.messages[0].content == "Kysymys"
        assert chat_repository.messages[1].content == llm_service.answer

    async def test_question_is_embedded_and_search_uses_document_and_top_k_5(
        self, document, document_repository, chat_repository, embedding_service, llm_service
    ) -> None:
        use_case, chunk_repository = _prepare(
            document_repository=document_repository,
            chat_repository=chat_repository,
            embedding_service=embedding_service,
            llm_service=llm_service,
        )

        await use_case.execute(
            question="  Mitä dokumentissa sanotaan?  ", document_id=document.id
        )

        # Kysymys upotetaan (trimmattuna) ja haku kohdistetaan dokumenttiin
        assert embedding_service.texts == ["Mitä dokumentissa sanotaan?"]
        assert len(chunk_repository.search_calls) == 1
        call = chunk_repository.search_calls[0]
        assert call["query_embedding"] == [0.25, 0.75]
        assert call["document_id"] == document.id
        assert call["top_k"] == 5

    async def test_llm_receives_question_and_context_with_chunk_contents(
        self, document, document_repository, chat_repository, embedding_service, llm_service
    ) -> None:
        chunk1 = _make_chunk(document.id, index=0, content="Ensimmäinen palanen")
        chunk2 = _make_chunk(document.id, index=1, content="Toinen palanen")
        use_case, _ = _prepare(
            document_repository=document_repository,
            chat_repository=chat_repository,
            embedding_service=embedding_service,
            llm_service=llm_service,
            results=[(chunk1, 0.9), (chunk2, 0.7)],
        )

        await use_case.execute(
            question="Mitä dokumentissa sanotaan?", document_id=document.id
        )

        assert len(llm_service.calls) == 1
        assert llm_service.calls[0]["question"] == "Mitä dokumentissa sanotaan?"
        context = llm_service.calls[0]["context"]
        assert "[Lähde 1]" in context
        assert "[Lähde 2]" in context
        assert "Ensimmäinen palanen" in context
        assert "Toinen palanen" in context

    async def test_creates_new_session_with_question_as_title(
        self, document, document_repository, chat_repository, embedding_service, llm_service
    ) -> None:
        use_case, _ = _prepare(
            document_repository=document_repository,
            chat_repository=chat_repository,
            embedding_service=embedding_service,
            llm_service=llm_service,
        )

        result = await use_case.execute(
            question="Mikä on dokumentin pääasia?", document_id=document.id
        )

        assert len(chat_repository.created_sessions) == 1
        session = chat_repository.created_sessions[0]
        assert result.session.id == session.id
        assert session.document_id == document.id
        assert session.title == "Mikä on dokumentin pääasia?"

    async def test_custom_top_k_is_passed_to_similarity_search(
        self, document, document_repository, chat_repository, embedding_service, llm_service
    ) -> None:
        use_case, chunk_repository = _prepare(
            document_repository=document_repository,
            chat_repository=chat_repository,
            embedding_service=embedding_service,
            llm_service=llm_service,
            top_k=3,
        )

        await use_case.execute(question="Kysymys", document_id=document.id)

        assert chunk_repository.search_calls[0]["top_k"] == 3


class TestChatUseCaseNoResults:
    """Ei hakutuloksia: tarkka "ei tietoa" -lause ilman kielimallikutsua."""

    async def test_returns_exact_fallback_without_llm_call(
        self, document, document_repository, chat_repository, embedding_service, llm_service
    ) -> None:
        use_case, chunk_repository = _prepare(
            document_repository=document_repository,
            chat_repository=chat_repository,
            embedding_service=embedding_service,
            llm_service=llm_service,
            results=[],
        )

        result = await use_case.execute(
            question="Kysymys johon ei ole vastausta", document_id=document.id
        )

        assert result.message.content == NO_INFO_ANSWER
        assert result.message.sources == []
        assert llm_service.calls == []
        assert len(chunk_repository.search_calls) == 1
        # Viestit tallennetaan myös fallback-vastauksella
        assert [m.role for m in chat_repository.messages] == [
            ChatRole.USER,
            ChatRole.ASSISTANT,
        ]


class TestChatUseCaseSessions:
    """Istuntojen hallinta: uusi, jatkettava ja virhetilanteet."""

    async def test_existing_session_is_reused(
        self, document, document_repository, embedding_service, llm_service
    ) -> None:
        session = ChatSession(id=uuid4(), document_id=document.id, title="Aihe")
        chat_repository = FakeChatRepository([session])
        use_case, _ = _prepare(
            document_repository=document_repository,
            chat_repository=chat_repository,
            embedding_service=embedding_service,
            llm_service=llm_service,
        )

        result = await use_case.execute(
            question="Jatkokysymys", document_id=document.id, session_id=session.id
        )

        assert result.session.id == session.id
        assert chat_repository.created_sessions == []
        assert all(m.session_id == session.id for m in chat_repository.messages)

    async def test_unknown_session_raises_not_found(
        self, document, document_repository, embedding_service, llm_service
    ) -> None:
        chat_repository = FakeChatRepository([])
        use_case, _ = _prepare(
            document_repository=document_repository,
            chat_repository=chat_repository,
            embedding_service=embedding_service,
            llm_service=llm_service,
        )

        with pytest.raises(NotFoundError):
            await use_case.execute(
                question="Kysymys", document_id=document.id, session_id=uuid4()
            )

        assert chat_repository.messages == []

    async def test_session_bound_to_other_document_raises_validation_error(
        self, document, document_repository, embedding_service, llm_service
    ) -> None:
        other_document = _make_document()
        session = ChatSession(id=uuid4(), document_id=other_document.id, title="Väärä")
        chat_repository = FakeChatRepository([session])
        use_case, _ = _prepare(
            document_repository=document_repository,
            chat_repository=chat_repository,
            embedding_service=embedding_service,
            llm_service=llm_service,
        )

        with pytest.raises(ValidationError):
            await use_case.execute(
                question="Kysymys", document_id=document.id, session_id=session.id
            )


class TestChatUseCaseErrors:
    """Syötteen ja resurssien validointi ennen kutsuja."""

    async def test_unknown_document_raises_not_found(
        self, document_repository, chat_repository, embedding_service, llm_service
    ) -> None:
        use_case, _ = _prepare(
            document_repository=document_repository,
            chat_repository=chat_repository,
            embedding_service=embedding_service,
            llm_service=llm_service,
        )

        with pytest.raises(NotFoundError):
            await use_case.execute(question="Kysymys", document_id=uuid4())

        # Ei kutsuja ulkoisiin palveluihin puuttuvalle dokumentille
        assert embedding_service.texts == []
        assert llm_service.calls == []

    async def test_blank_question_raises_validation_error(
        self, document, document_repository, chat_repository, embedding_service, llm_service
    ) -> None:
        use_case, chunk_repository = _prepare(
            document_repository=document_repository,
            chat_repository=chat_repository,
            embedding_service=embedding_service,
            llm_service=llm_service,
        )

        with pytest.raises(ValidationError):
            await use_case.execute(question="   ", document_id=document.id)

        assert embedding_service.texts == []
        assert chunk_repository.search_calls == []
