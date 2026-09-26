# =============================================================================
# Presentation — chat-reitti (RAG-kysely dokumentilta)
# Vastaanottaa kysymyksen + dokumentin tunnuksen, hakee relevantimmat chunkit
# (top 5), generoi vastauksen vain ladattuun materiaaliin vedoten ja palauttaa
# sen lähteineen JSONina.
# =============================================================================
from __future__ import annotations

from fastapi import APIRouter, Depends

from app.application.dtos.chat_dto import ChatMessageDTO, ChatRequestDTO, ChatResponseDTO
from app.application.use_cases.chat_with_document import ChatWithDocumentUseCase
from app.presentation.dependencies import get_chat_with_document_use_case

router = APIRouter()


@router.post(
    "",
    response_model=ChatResponseDTO,
    summary="Kysy dokumentilta (RAG)",
)
async def chat(
    payload: ChatRequestDTO,
    use_case: ChatWithDocumentUseCase = Depends(get_chat_with_document_use_case),
) -> ChatResponseDTO:
    """Vastaa kysymykseen dokumentin sisällön perusteella ja palauttaa lähteet.

    Prosessi:
      1. Luo embedding kysymyksestä (text-embedding-3-small)
      2. Hae 5 relevantinta chunkkia (pgvector, cosine-etäisyys)
      3. Muodosta konteksti → LLM vastaa vain materiaalin perusteella
         (ei tietoa → tarkka "ei tietoa" -lause)
      4. Tallenna viestit + lähteet, palauta JSON
    """
    result = await use_case.execute(
        question=payload.question,
        document_id=payload.document_id,
        session_id=payload.session_id,
    )

    return ChatResponseDTO(
        session_id=result.session.id,
        message=ChatMessageDTO.from_entity(result.message),
    )