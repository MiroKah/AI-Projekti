# =============================================================================
# Use case — keskustelu dokumentin kanssa (RAG-kysely)
#
# Vaiheet:
#   1. Validoidaan syöte ja haetaan kohdedokumentti (DocumentRepository)
#   2. Luo embedding kysymyksestä (EmbeddingService)
#   3. Vektorihaku: hae 5 relevanteimmat chunkkia (ChunkRepository, pgvector)
#   4. Rakenna konteksti haetuista chunkeista ja generoi vastaus (LLMService).
#      Jos hakutuloksia ei ole, palautetaan suoraan "ei tietoa" -vastaus
#      ilman kielimallikutsua.
#   5. Tallenna käyttäjän viesti ja assistentin vastaus + lähteet (ChatRepository)
# =============================================================================
from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from uuid import UUID, uuid4

from app.core.constants import NO_INFO_ANSWER
from app.core.exceptions import NotFoundError, ValidationError
from app.core.logging import get_logger
from app.domain.entities.chat import ChatMessage, ChatRole, ChatSession, SourceReference
from app.domain.entities.chunk import Chunk
from app.domain.interfaces.repositories import (
    ChatRepository,
    ChunkRepository,
    DocumentRepository,
)
from app.domain.interfaces.services import EmbeddingService, LLMService

logger = get_logger(__name__)

# Lähdeviittauksen ote näkymää varten (lyhyt ote chunkin sisällöstä)
_SNIPPET_LENGTH = 200

# Uuden keskusteluistunnon otsikko: kysymyksen alku
_SESSION_TITLE_LENGTH = 100


@dataclass(slots=True)
class ChatResult:
    """RAG-kyselyn tulos: istunto ja generoitu assistentin viesti (lähteineen)."""

    session: ChatSession
    message: ChatMessage


class ChatWithDocumentUseCase:
    """Vastaa käyttäjän kysymykseen dokumentin sisällön perusteella (RAG)."""

    def __init__(
        self,
        *,
        document_repository: DocumentRepository,
        chunk_repository: ChunkRepository,
        chat_repository: ChatRepository,
        embedding_service: EmbeddingService,
        llm_service: LLMService,
        retrieval_top_k: int = 5,
    ) -> None:
        self._documents = document_repository
        self._chunks = chunk_repository
        self._chat = chat_repository
        self._embeddings = embedding_service
        self._llm = llm_service
        self._top_k = retrieval_top_k

    async def execute(
        self,
        *,
        question: str,
        document_id: UUID,
        session_id: UUID | None = None,
    ) -> ChatResult:
        """Suorita RAG-kysely: embedding → vektorihaku → konteksti → LLM → tallennus."""
        question = question.strip()
        if not question:
            raise ValidationError("Kysymys ei voi olla tyhjä")

        document = await self._documents.get(document_id)
        if document is None:
            raise NotFoundError(f"Dokumenttia {document_id} ei löydy")

        # 1. Embedding kysymyksestä (text-embedding-3-small)
        query_embedding = await self._embeddings.embed_text(question)

        # 2. Vektorihaku: 5 relevanteimmin chunkkia tästä dokumentista (cosine)
        results = await self._chunks.similarity_search(
            query_embedding,
            document_id=document_id,
            top_k=self._top_k,
        )
        logger.info("%s hakutulosta kysymykseen (document_id=%s)", len(results), document_id)

        # 3-4. Vastaus vain ladattuun materiaaliin vedoten. Jos materiaalia ei
        #      löydy, palautetaan tarkka "ei tietoa" -lause ilman kielimallikutsua.
        if results:
            context = self._build_context(results)
            answer = await self._llm.generate_answer(question=question, context=context)
        else:
            logger.info("Ei hakutuloksia — vastaus palautetaan ilman kielimallikutsua")
            answer = NO_INFO_ANSWER

        # 5. Istunto: jatka olemassa olevaa tai luo uusi
        session = await self._resolve_session(
            question=question,
            document_id=document_id,
            session_id=session_id,
        )

        # 6. Tallenna viestit: käyttäjän kysymys ja assistentin vastaus lähteineen
        await self._chat.add_message(
            ChatMessage(
                id=uuid4(),
                session_id=session.id,
                role=ChatRole.USER,
                content=question,
            )
        )
        assistant_message = await self._chat.add_message(
            ChatMessage(
                id=uuid4(),
                session_id=session.id,
                role=ChatRole.ASSISTANT,
                content=answer,
                sources=[self._to_source(chunk, score) for chunk, score in results],
            )
        )

        return ChatResult(session=session, message=assistant_message)

    @staticmethod
    def _build_context(results: Sequence[tuple[Chunk, float]]) -> str:
        """Muodosta numeroidut lähteet sisältävä konteksti-merkkijono LLM:lle."""
        parts = []
        for number, (chunk, score) in enumerate(results, start=1):
            parts.append(
                f"[Lähde {number}] (chunk #{chunk.chunk_index}, "
                f"samankaltaisuus {score:.3f})\n{chunk.content}"
            )
        return "\n\n".join(parts)

    async def _resolve_session(
        self, *, question: str, document_id: UUID, session_id: UUID | None
    ) -> ChatSession:
        """Palauta jatkettava istunto: luo uusi tai hae ja valido olemassa oleva."""
        if session_id is None:
            session = await self._chat.create_session(
                ChatSession(
                    id=uuid4(),
                    document_id=document_id,
                    title=question[:_SESSION_TITLE_LENGTH],
                )
            )
            logger.info("Uusi keskusteluistunto luotu (id=%s)", session.id)
            return session

        session = await self._chat.get_session(session_id)
        if session is None:
            raise NotFoundError(f"Keskusteluistuntoa {session_id} ei löydy")
        if session.document_id is not None and session.document_id != document_id:
            raise ValidationError("Keskusteluistunto on liitetty toiseen dokumenttiin")
        return session

    @staticmethod
    def _to_source(chunk: Chunk, score: float) -> SourceReference:
        """Muunna hakutulos lähteenviittaukseksi (lyhyt ote + samankaltaisuuspisteet)."""
        snippet = chunk.content[:_SNIPPET_LENGTH]
        if len(chunk.content) > _SNIPPET_LENGTH:
            snippet += "…"
        return SourceReference(
            chunk_id=chunk.id,
            document_id=chunk.document_id,
            chunk_index=chunk.chunk_index,
            snippet=snippet,
            score=score,
        )