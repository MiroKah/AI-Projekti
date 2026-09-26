// =============================================================================
// Chat-sivu /chat/[id]: keskustelu yhtä dokumenttia vasten (RAG)
// =============================================================================
"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { ArrowLeft, FileText, Info } from "lucide-react";

import { ChatPanel } from "@/components/chat/chat-panel";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { documentsApi } from "@/lib/api";
import { errorMessage } from "@/lib/utils";
import type { DocumentItem, DocumentStatus } from "@/types";

const STATUS_META: Record<DocumentStatus, { label: string; variant: "success" | "warning" | "secondary" | "destructive" }> = {
  ready: { label: "Valmis", variant: "success" },
  processing: { label: "Käsitellään", variant: "warning" },
  pending: { label: "Odottaa", variant: "secondary" },
  failed: { label: "Epäonnistui", variant: "destructive" },
};

export default function ChatPage() {
  const params = useParams<{ id: string }>();
  const documentId = params?.id;

  const [document, setDocument] = useState<DocumentItem | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!documentId) {
      setLoading(false);
      setError("Dokumentin tunniste puuttuu osoitteesta.");
      return;
    }

    let cancelled = false;
    void (async () => {
      try {
        const result = await documentsApi.get(documentId);
        if (!cancelled) {
          setDocument(result);
          setError(null);
        }
      } catch (err) {
        if (!cancelled) setError(errorMessage(err));
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [documentId]);

  // Lataustila
  if (loading) {
    return (
      <div className="flex flex-col gap-4" aria-busy="true" aria-label="Ladataan dokumenttia">
        <Skeleton className="h-8 w-2/3" />
        <Skeleton className="h-4 w-1/3" />
        <Skeleton className="h-80 w-full rounded-xl" />
      </div>
    );
  }

  // Virhe (esim. dokumentti ei löydy / backend ei vastaa)
  if (error || !documentId || !document) {
    return (
      <div className="mx-auto max-w-xl py-10">
        <Alert variant="destructive">
          <AlertTitle>Keskustelua ei voitu avata</AlertTitle>
          <AlertDescription>
            {error ?? "Dokumenttia ei voitu ladata. Tarkista, että backend on käynnissä."}
          </AlertDescription>
        </Alert>
        <div className="mt-4 flex gap-2">
          <Link href="/chat" className="inline-flex items-center gap-1.5 text-sm text-primary hover:underline">
            <ArrowLeft className="size-4" aria-hidden="true" /> Takaisin listaan
          </Link>
          <span aria-hidden="true">·</span>
          <Link href="/upload" className="text-sm text-primary hover:underline">
            Lataa dokumentti
          </Link>
        </div>
      </div>
    );
  }

  const status = STATUS_META[document.status];
  const notReady = document.status !== "ready";

  return (
    <div className="flex flex-col gap-4">
      {/* Otsikko: takaisin + dokumentin tiedot */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="min-w-0">
          <Link
            href="/chat"
            className="inline-flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground"
          >
            <ArrowLeft className="size-4" aria-hidden="true" /> Kaikki dokumentit
          </Link>
          <h1 className="mt-1 flex items-center gap-2 text-xl font-bold tracking-tight">
            <FileText className="size-5 shrink-0 text-muted-foreground" aria-hidden="true" />
            <span className="truncate">{document.title ?? document.filename}</span>
            <Badge variant={status.variant}>{status.label}</Badge>
          </h1>
        </div>
      </div>

      {notReady && (
        <Alert variant="warning">
          <Info aria-hidden="true" />
          <AlertTitle>Dokumenttia ei ole vielä indeksoitu</AlertTitle>
          <AlertDescription>
            Kysymyksiin voi vastata vasta kun dokumentti on valmis. Tarkista tila hetken kuluttua
            päivittämällä sivu.
          </AlertDescription>
        </Alert>
      )}

      {/* Keskustelu */}
      <div className="min-h-[32rem]">
        <ChatPanel documentId={documentId} key={documentId} />
      </div>
    </div>
  );
}
