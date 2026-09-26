// =============================================================================
// Lataussivu: PDF-nouto + indeksointi + oman dokumenttilistan hallinta
// =============================================================================
"use client";

import { FileUp } from "lucide-react";

import { DocumentList } from "@/components/documents/document-list";
import { DocumentUpload } from "@/components/documents/document-upload";
import { Button } from "@/components/ui/button";
import { useDocuments } from "@/hooks/use-documents";

export default function UploadPage() {
  const { documents, loading, error, refresh, remove } = useDocuments();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="flex items-center gap-2 text-2xl font-bold tracking-tight">
          <FileUp className="size-6" aria-hidden="true" /> Lataa PDF
        </h1>
        <p className="mt-1 max-w-xl text-sm text-muted-foreground">
          Lataa oppimateriaalisi (esim. luentomoniste tai opaskirja). Dokumentti pilkotaan,
          upotetaan ja indeksoidaan, minkä jälkeen voit keskustella sen sisällöstä.
        </p>
      </div>

      <DocumentUpload onUploaded={() => void refresh()} />

      <section className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">Omat dokumentit</h2>
          <Button
            variant="outline"
            size="sm"
            onClick={() => void refresh()}
            disabled={loading}
          >
            Päivitä
          </Button>
        </div>
        <DocumentList
          documents={documents}
          loading={loading}
          error={error}
          onRetry={() => void refresh()}
          onDelete={(document) => remove(document.id)}
        />
      </section>
    </div>
  );
}
