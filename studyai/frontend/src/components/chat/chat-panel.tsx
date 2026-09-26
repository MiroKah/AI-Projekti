// =============================================================================
// StudyAI — keskustelupaneeli (RAG-kysely valitulta dokumentilta)
// Lähdechunkit näytetään vastauksen alla (backend palauttaa ne message.sources).
// =============================================================================
"use client";

import { useRef, useState, type FormEvent } from "react";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Spinner } from "@/components/ui/spinner";
import { toast } from "@/hooks/use-toast";
import { chatApi } from "@/lib/api";
import { errorMessage } from "@/lib/utils";
import type { ChatMessage } from "@/types";

interface ChatPanelProps {
  /** Valittu dokumentti, jonka sisällöstä keskustellaan. */
  documentId?: string | null;
}

export function ChatPanel({ documentId }: ChatPanelProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  // Jatketaan samaa istuntoa seuraavissa viesteissä (session_id ensimmäisestä vastauksesta)
  const sessionIdRef = useRef<string | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    // Keskustelu vaatii aina valitun dokumentin (backend hakee chunkit sen id:llä)
    if (!question.trim() || !documentId || loading) return;

    setLoading(true);
    setError(null);
    try {
      const response = await chatApi.ask({
        question: question.trim(),
        document_id: documentId,
        session_id: sessionIdRef.current ?? undefined,
      });
      sessionIdRef.current = response.session_id;
      setMessages((previous) => [...previous, response.message]);
      setQuestion("");
    } catch (err) {
      const message = errorMessage(err);
      setError(message);
      toast.error("Kysymys epäonnistui", message);
    } finally {
      setLoading(false);
    }
  }

  function clearConversation() {
    setMessages([]);
    setError(null);
    setQuestion("");
    sessionIdRef.current = null;
  }

  return (
    <div className="flex h-full flex-col gap-4">
      <div className="flex-1 space-y-3 overflow-y-auto">
        {error && (
          <Alert variant="destructive">
            <AlertTitle>Kysymys epäonnistui</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}
        {messages.length === 0 && !error && (
          <p className="text-sm text-muted-foreground">
            Esitä kysymys valitusta dokumentista — vastaus perustuu vain ladattuun
            materiaaliin.
          </p>
        )}
        {messages.map((message) => (
          <div key={message.id} className="rounded-lg border p-3 text-sm">
            <span className="font-semibold">{message.role}: </span>
            {message.content}
            {message.sources.length > 0 && (
              <div className="mt-2 space-y-1 border-t pt-2 text-xs text-muted-foreground">
                {message.sources.map((source) => (
                  <p key={source.chunk_id}>
                    Lähde {source.chunk_index}: {source.snippet}
                    {source.score != null &&
                      ` — samankaltaisuus ${(source.score * 100).toFixed(0)} %`}
                  </p>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="flex items-center justify-between">
        <p className="text-xs text-muted-foreground">
          {messages.length > 0 && `${messages.length} viestiä`}
        </p>
        {messages.length > 0 && (
          <button
            type="button"
            onClick={clearConversation}
            className="text-xs text-muted-foreground underline-offset-4 hover:text-foreground hover:underline"
          >
            Tyhjennä keskustelu
          </button>
        )}
      </div>

      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          className="flex-1 rounded-md border px-3 py-2 text-sm"
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder={documentId ? "Kysy dokumentista..." : "Valitse ensin dokumentti"}
          disabled={loading || !documentId}
          aria-label="Kysymys dokumentille"
        />
        <button
          type="submit"
          className="inline-flex items-center gap-2 rounded-md bg-primary px-4 py-2 text-sm text-primary-foreground disabled:opacity-50"
          disabled={loading || !documentId}
          aria-busy={loading}
        >
          {loading && <Spinner label="" className="text-primary-foreground" />}
          {loading ? "Lähetetään…" : "Lähetä"}
        </button>
      </form>
    </div>
  );
}