// =============================================================================
// DocumentList: dokumenttilista (loading / error / empty / toiminnot)
// Käytetään etusivulla ja lataussivulla.
// =============================================================================
"use client";

import { useState } from "react";
import Link from "next/link";
import { FileText, MessageSquare, RefreshCw, Trash2, UploadCloud } from "lucide-react";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button, buttonVariants } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { toast } from "@/hooks/use-toast";
import { errorMessage, formatBytes, formatDate } from "@/lib/utils";
import type { DocumentItem, DocumentStatus } from "@/types";

interface StatusMeta {
  label: string;
  variant: "success" | "warning" | "secondary" | "destructive";
}

const STATUS_META: Record<DocumentStatus, StatusMeta> = {
  ready: { label: "Valmis", variant: "success" },
  processing: { label: "Käsitellään", variant: "warning" },
  pending: { label: "Odottaa", variant: "secondary" },
  failed: { label: "Epäonnistui", variant: "destructive" },
};

interface DocumentListProps {
  documents: DocumentItem[];
  loading?: boolean;
  error?: string | null;
  /** Kutsutaan virhetilanteessa (esim. "yritä uudelleen"). */
  onRetry?: () => void;
  /** Suorittaa dokumentin poiston (esim. tietokantahakemuksen läpi). */
  onDelete?: (document: DocumentItem) => Promise<void>;
  emptyTitle?: string;
  emptyDescription?: string;
}

export function DocumentList({
  documents,
  loading = false,
  error = null,
  onRetry,
  onDelete,
  emptyTitle = "Ei dokumentteja vielä",
  emptyDescription = "Lataa ensimmäinen PDF-materiaalisi ja aloita keskustelu.",
}: DocumentListProps) {
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [confirmId, setConfirmId] = useState<string | null>(null);

  async function handleDelete(document: DocumentItem) {
    if (!onDelete) return;
    setDeletingId(document.id);
    try {
      await onDelete(document);
      toast.success("Dokumentti poistettu", document.filename);
      setConfirmId(null);
    } catch (err) {
      toast.error("Poisto epäonnistui", errorMessage(err));
    } finally {
      setDeletingId(null);
    }
  }

  if (loading) {
    return (
      <div className="space-y-3" aria-busy="true" aria-label="Ladataan dokumentteja">
        {Array.from({ length: 3 }).map((_, index) => (
          <div key={index} className="flex items-center gap-3 rounded-lg border p-4">
            <Skeleton className="size-9 rounded-lg" />
            <div className="flex-1 space-y-2">
              <Skeleton className="h-4 w-2/3" />
              <Skeleton className="h-3 w-1/3" />
            </div>
            <Skeleton className="h-5 w-16 rounded-md" />
          </div>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertTitle>Dokumentteja ei voitu ladata</AlertTitle>
        <AlertDescription className="flex flex-wrap items-center justify-between gap-3">
          <span>{error}</span>
          {onRetry && (
            <Button variant="outline" size="sm" onClick={onRetry}>
              <RefreshCw aria-hidden="true" /> Yritä uudelleen
            </Button>
          )}
        </AlertDescription>
      </Alert>
    );
  }

  if (documents.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center gap-3 rounded-xl border border-dashed p-10 text-center">
        <span className="flex size-12 items-center justify-center rounded-full bg-muted">
          <UploadCloud className="size-6 text-muted-foreground" aria-hidden="true" />
        </span>
        <div>
          <p className="font-medium">{emptyTitle}</p>
          <p className="mt-1 text-sm text-muted-foreground">{emptyDescription}</p>
        </div>
        <Link href="/upload" className={buttonVariants({ size: "sm" })}>
          Lataa PDF
        </Link>
      </div>
    );
  }

  return (
    <ul className="space-y-3">
      {documents.map((document) => {
        const status = STATUS_META[document.status];
        const chatEnabled = document.status === "ready";
        const isDeleting = deletingId === document.id;
        const isConfirming = confirmId === document.id;

        return (
          <li
            key={document.id}
            className="flex flex-col gap-3 rounded-xl border bg-card p-4 transition-shadow hover:shadow-md sm:flex-row sm:items-center sm:gap-4"
          >
            <span className="flex size-10 shrink-0 items-center justify-center rounded-lg bg-muted">
              <FileText className="size-5 text-muted-foreground" aria-hidden="true" />
            </span>

            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-medium">{document.filename}</p>
              <p className="mt-0.5 truncate text-xs text-muted-foreground">
                {formatDate(document.created_at)}
                {document.page_count != null && <> · {document.page_count} sivua</>}
                <> · {formatBytes(document.size_bytes)}</>
              </p>
            </div>

            <div className="flex shrink-0 items-center gap-2">
              <Badge variant={status.variant}>{status.label}</Badge>

              {chatEnabled ? (
                <Link
                  href={`/chat/${document.id}`}
                  className={buttonVariants({ variant: "outline", size: "icon" })}
                  aria-label={`Keskustele dokumentista ${document.filename}`}
                  title="Keskustele dokumentista"
                >
                  <MessageSquare aria-hidden="true" />
                </Link>
              ) : (
                <span
                  className={buttonVariants({ variant: "outline", size: "icon" })}
                  aria-disabled="true"
                  title="Dokumenttia ei ole vielä indeksoitu"
                >
                  <MessageSquare aria-hidden="true" className="opacity-40" />
                </span>
              )}

              {isConfirming ? (
                <span className="flex items-center gap-1">
                  <Button
                    variant="destructive"
                    size="sm"
                    disabled={isDeleting}
                    onClick={() => void handleDelete(document)}
                  >
                    {isDeleting ? "Poistetaan…" : "Poista"}
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setConfirmId(null)}
                    disabled={isDeleting}
                  >
                    Peruuta
                  </Button>
                </span>
              ) : (
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => setConfirmId(document.id)}
                  aria-label={`Poista dokumentti ${document.filename}`}
                  title="Poista"
                >
                  <Trash2 aria-hidden="true" className="text-muted-foreground" />
                </Button>
              )}
            </div>
          </li>
        );
      })}
    </ul>
  );
}
