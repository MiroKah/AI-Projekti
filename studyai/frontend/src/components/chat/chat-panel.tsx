// =============================================================================
// StudyAI — keskustelupaneeli (runko)
// Varsinainen toteutus lisätään seuraavassa vaiheessa.
// =============================================================================
"use client";

import type { FormEvent } from "react";
import { useState } from "react";

import { chatApi } from "@/lib/api";
import type { ChatMessage } from "@/types";

interface ChatPanelProps {
  /** Valittu dokumentti, jonka sisällöstä keskustellaan. */
  documentId?: string | null;
}

export function ChatPanel({ documentId }: ChatPanelProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!question.trim()) return;

    setLoading(true);
    try {
      // Varsinainen kutsu; backend vastaa 501 toistaiseksi.
      const response = await chatApi.ask({
        question,
        document_id: documentId ?? null,
      });
      setMessages((prev) => [...prev, response.message]);
      setQuestion("");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex h-full flex-col gap-4">
      <div className="flex-1 space-y-3 overflow-y-auto">
        {messages.length === 0 && (
          <p className="text-sm text-muted-foreground">
            Esitä kysymys valitusta dokumentista.
          </p>
        )}
        {messages.map((message) => (
          <div key={message.id} className="rounded-lg border p-3 text-sm">
            <span className="font-semibold">{message.role}: </span>
            {message.content}
          </div>
        ))}
      </div>

      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          className="flex-1 rounded-md border px-3 py-2 text-sm"
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder="Kysy dokumentista..."
          disabled={loading}
        />
        <button
          type="submit"
          className="rounded-md bg-primary px-4 py-2 text-sm text-primary-foreground"
          disabled={loading}
        >
          Lähetä
        </button>
      </form>
    </div>
  );
}