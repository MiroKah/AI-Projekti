// =============================================================================
// Keskustelun valitsin: valitse indeksoitu dokumentti ja siirry keskusteluun
// =============================================================================
"use client";

import Link from "next/link";
import { MessagesSquare } from "lucide-react";

import { DocumentList } from "@/components/documents/document-list";
import { Button } from "@/components/ui/button";
import { useDocuments } from "@/hooks/use-documents";

export default function ChatIndexPage() {
  const { documents, loading, error, refresh, remove } = useDocuments();
  const readyCount = documents.filter((document) => document.status === "ready").length;

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="flex items-center gap-2 text-2xl font-bold tracking-tight">
            <MessagesSquare className="size-6" aria-hidden="true" /> Keskustelu
          </h1>
          <p className="mt-1 max-w-xl text-sm text-muted-foreground">
            Valitse indeksoitu dokumentti ja aloita siitä kysyminen. Voit myös jatkaa
            aikaisempaa keskustelua dokumenttilistasta.
          </p>
        </div>
        <div className="text-sm text-muted-foreground">
          {loading ? "Ladataan…" : `${readyCount} valmiina keskusteluun`}
        </div>
      </div>

      <DocumentList
        documents={documents}
        loading={loading}
        error={error}
        onRetry={() => void refresh()}
        onDelete={(document) => remove(document.id)}
        emptyTitle="Ei vielä keskusteltavia dokumentteja"
        emptyDescription="Lataa ensin PDF, odota sen indeksointia ja aloita sitten keskustelu."
      />

      <div className="text-center">
        <Link href="/upload">
          <Button variant="outline" size="sm">
            Lataa uusi dokumentti
          </Button>
        </Link>
      </div>
    </div>
  );
}
