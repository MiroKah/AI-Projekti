# =============================================================================
# Testit — /api/documents -reitit (lataus, listaus, haku, poisto)
# Käyttää FastAPI:n dependency overridea: ei tietokantaa eikä OpenAIia.
# =============================================================================
from __future__ import annotations

from collections.abc import Sequence
from uuid import uuid4

from app.application.use_cases.upload_document import IndexDocumentResult
from app.core.exceptions import NotFoundError
from app.domain.entities.document import Document, DocumentStatus
from app.presentation.api.v1.router import api_router
from app.presentation.dependencies import get_document_repository, get_upload_document_use_case
from app.presentation.middleware import register_exception_handlers
from fastapi import FastAPI
from fastapi.testclient import TestClient


class FakeDocumentRepository:
    """Muistinvarainen DocumentRepository-fake testejä varten."""

    def __init__(self, documents: Sequence[Document] = ()) -> None:
        self.documents = {document.id: document for document in documents}

    async def add(self, document: Document) -> Document:
        self.documents[document.id] = document
        return document

    async def get(self, document_id):
        return self.documents.get(document_id)

    async def list(self) -> Sequence[Document]:
        return list(self.documents.values())

    async def update(self, document: Document) -> Document:
        self.documents[document.id] = document
        return document

    async def delete(self, document_id) -> None:
        self.documents.pop(document_id, None)


class FakeUploadUseCase:
    """Palauttaa valmiin indeksointituloksen ilman tietokantaa/OpenAIia."""

    async def execute(self, *, filename: str, file_bytes: bytes, title: str | None = None):
        document = Document(
            id=uuid4(),
            filename=filename,
            title=title,
            size_bytes=len(file_bytes),
            page_count=3,
            status=DocumentStatus.READY,
        )
        return IndexDocumentResult(document=document, chunks_created=7)


def _make_client(repository: FakeDocumentRepository) -> TestClient:
    """Rakentaa testattavan sovelluksen (reitit + poikkeuskäsittelijät + DI-overridet)."""
    app = FastAPI(title="test")
    app.include_router(api_router, prefix="/api")
    register_exception_handlers(app)
    app.dependency_overrides[get_document_repository] = lambda: repository
    app.dependency_overrides[get_upload_document_use_case] = lambda: FakeUploadUseCase()
    return TestClient(app)


def test_list_documents_returns_items_and_total() -> None:
    document = Document(id=uuid4(), filename="kirja.pdf", status=DocumentStatus.READY)
    client = _make_client(FakeDocumentRepository([document]))

    response = client.get("/api/documents")

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["filename"] == "kirja.pdf"
    assert body["items"][0]["status"] == "ready"


def test_upload_validates_pdf_and_creates_document() -> None:
    client = _make_client(FakeDocumentRepository())

    response = client.post(
        "/api/documents",
        files={"file": ("kirja.pdf", b"%PDF-1.4 sisalto", "application/pdf")},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["document"]["filename"] == "kirja.pdf"
    assert body["document"]["status"] == "ready"
    assert body["chunks_created"] == 7


def test_upload_rejects_non_pdf() -> None:
    client = _make_client(FakeDocumentRepository())

    response = client.post(
        "/api/documents",
        files={"file": ("muistiinpano.txt", b"eipdf", "text/plain")},
    )

    assert response.status_code == 422
    assert "PDF" in response.json()["detail"]


def test_get_document_returns_document() -> None:
    document = Document(id=uuid4(), filename="lento.pdf", status=DocumentStatus.PENDING)
    client = _make_client(FakeDocumentRepository([document]))

    response = client.get(f"/api/documents/{document.id}")

    assert response.status_code == 200
    assert response.json()["filename"] == "lento.pdf"


def test_get_unknown_document_returns_404() -> None:
    client = _make_client(FakeDocumentRepository())

    response = client.get(f"/api/documents/{uuid4()}")

    assert response.status_code == 404
    assert response.json()["error"] == NotFoundError.__name__


def test_delete_returns_204_and_removes_document() -> None:
    document = Document(id=uuid4(), filename="vanha.pdf")
    repository = FakeDocumentRepository([document])
    client = _make_client(repository)

    response = client.delete(f"/api/documents/{document.id}")

    assert response.status_code == 204
    assert response.content == b""
    assert document.id not in repository.documents


def test_delete_unknown_document_returns_404() -> None:
    client = _make_client(FakeDocumentRepository())

    response = client.delete(f"/api/documents/{uuid4()}")

    assert response.status_code == 404
