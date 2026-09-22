-- =============================================================================
-- StudyAI — PostgreSQL / pgvector alustus
-- Ajetaan automaattisesti, kun tietokantasäiliö käynnistetään ensimmäisen kerran.
-- =============================================================================

-- pgvector-laajennos (vektorihaut varten)
CREATE EXTENSION IF NOT EXISTS vector;

-- UUID-generaattori (gen_random_uuid)
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- -----------------------------------------------------------------------------
-- documents: ladatut PDF-dokumentit
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS documents (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filename     TEXT        NOT NULL,
    title        TEXT,
    page_count   INTEGER,
    size_bytes   BIGINT,
    status       TEXT        NOT NULL DEFAULT 'pending', -- pending | processing | ready | failed
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- -----------------------------------------------------------------------------
-- chunks: pilkotut tekstinpalaset + niiden embedding-vektorit
-- Oletusulottuvuus 1536 (text-embedding-3-small). Muuta tarvittaessa.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS chunks (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id  UUID        NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index  INTEGER     NOT NULL,
    content      TEXT        NOT NULL,
    token_count  INTEGER,
    embedding    vector(1536),
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Nopeat haut dokumentin mukaan
CREATE INDEX IF NOT EXISTS idx_chunks_document_id ON chunks (document_id);

-- Vektorihaku (HNSW-indeksi kosinietäisyydelle)
CREATE INDEX IF NOT EXISTS idx_chunks_embedding_hnsw
    ON chunks USING hnsw (embedding vector_cosine_ops);

-- -----------------------------------------------------------------------------
-- chat_sessions: keskusteluistunnot
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS chat_sessions (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id  UUID        REFERENCES documents(id) ON DELETE CASCADE,
    title        TEXT,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- -----------------------------------------------------------------------------
-- chat_messages: yksittäiset viestit istunnossa
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS chat_messages (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id   UUID        NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    role         TEXT        NOT NULL, -- user | assistant | system
    content      TEXT        NOT NULL,
    sources      JSONB       NOT NULL DEFAULT '[]'::jsonb,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id ON chat_messages (session_id);

-- -----------------------------------------------------------------------------
-- updated_at-automaattipäivitys documents-tauluun
-- -----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_documents_updated_at ON documents;
CREATE TRIGGER trg_documents_updated_at
    BEFORE UPDATE ON documents
    FOR EACH ROW
    EXECUTE FUNCTION set_updated_at();