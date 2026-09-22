// =============================================================================
// StudyAI — jaetut TypeScript-tyypit (vastaavat backendin DTO:ita)
// =============================================================================

/** Dokumentin käsittelyn tila. */
export type DocumentStatus = "pending" | "processing" | "ready" | "failed";

/** Ladattu PDF-dokumentti. */
export interface DocumentItem {
  id: string;
  filename: string;
  title: string | null;
  page_count: number | null;
  size_bytes: number | null;
  status: DocumentStatus;
  created_at: string | null;
  updated_at: string | null;
}

/** Lista dokumenteista. */
export interface DocumentList {
  items: DocumentItem[];
  total: number;
}

/** PDF-latauksen tulos. */
export interface UploadResult {
  document: DocumentItem;
  chunks_created: number;
  message: string;
}

/** Lähdeviittaus vastauksessa. */
export interface SourceReference {
  chunk_id: string;
  document_id: string;
  chunk_index: number;
  snippet: string;
  score: number | null;
}

/** Viestin rooli. */
export type ChatRole = "user" | "assistant" | "system";

/** Yksittäinen chat-viesti. */
export interface ChatMessage {
  id: string;
  session_id: string;
  role: ChatRole;
  content: string;
  sources: SourceReference[];
  created_at: string | null;
}

/** Chat-pyynnön runko. */
export interface ChatRequest {
  question: string;
  document_id?: string | null;
  session_id?: string | null;
}

/** Chat-vastaus. */
export interface ChatResponse {
  session_id: string;
  message: ChatMessage;
}

/** Yhtenäinen API-virhe. */
export interface ApiError {
  error: string;
  detail: string;
}