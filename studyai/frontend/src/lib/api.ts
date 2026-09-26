// =============================================================================
// StudyAI — API-asiakas (selainpuoli)
// Kapseloi backend-kutsut ja virheenkäsittelyn.
// =============================================================================
import type {
  ChatRequest,
  ChatResponse,
  DocumentItem,
  DocumentList,
  UploadResult,
} from "@/types";

/** Backendin perusosoite (julkinen ympäristömuuttuja). */
const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

/** API-polun etuliite. */
const API_PREFIX = "/api";

/**
 * Geneerinen fetch-kääre, joka heittää virheen epäonnistuneesta vastauksesta.
 */
async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${API_PREFIX}${path}`, {
    headers:
      init?.body instanceof FormData
        ? undefined
        : { "Content-Type": "application/json" },
    ...init,
  });

  if (!response.ok) {
    const detail = await response.text().catch(() => response.statusText);
    throw new Error(`API-virhe (${response.status}): ${detail}`);
  }

  if (response.status === 204) return undefined as T;
  return (await response.json()) as T;
}

/** Dokumenttien API. */
export const documentsApi = {
  /** Listaa kaikki dokumentit. */
  list(): Promise<DocumentList> {
    return request<DocumentList>("/documents");
  },

  /** Hae yksittäinen dokumentti. */
  get(id: string): Promise<DocumentItem> {
    return request<DocumentItem>(`/documents/${id}`);
  },

  /** Lataa PDF-tiedosto. */
  upload(file: File): Promise<UploadResult> {
    const form = new FormData();
    form.append("file", file);
    return request<UploadResult>("/documents", { method: "POST", body: form });
  },

  /** Poista dokumentti. */
  remove(id: string): Promise<void> {
    return request<void>(`/documents/${id}`, { method: "DELETE" });
  },
};

/** Keskustelu-API. */
export const chatApi = {
  /** Lähetä kysymys dokumentilta (RAG). */
  ask(payload: ChatRequest): Promise<ChatResponse> {
    return request<ChatResponse>("/chat", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },
};