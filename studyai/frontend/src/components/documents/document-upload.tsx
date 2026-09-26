// =============================================================================
// DocumentUpload: PDF-lataus (drag & drop + tiedostovalinta) + indeksointitila
// =============================================================================
"use client";

import { useRef, useState, type ChangeEvent, type DragEvent } from "react";
import Link from "next/link";
import { FileCheck2, MessageSquare, UploadCloud } from "lucide-react";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button, buttonVariants } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import { toast } from "@/hooks/use-toast";
import { documentsApi } from "@/lib/api";
import { cn, errorMessage, formatBytes } from "@/lib/utils";
import type { UploadResult } from "@/types";

// Vastaa backendin MAX_UPLOAD_SIZE_MB-asetusta (backend tarkistaa lopullisesti)
const MAX_UPLOAD_SIZE_MB = 25;

function isPdfFile(file: File): boolean {
  return file.type === "application/pdf" || file.name.toLowerCase().endsWith(".pdf");
}

interface DocumentUploadProps {
  /** Kutsutaan onnistuneen indeksoinnin jälkeen (esim. listan päivitys). */
  onUploaded?: (result: UploadResult) => void;
}

export function DocumentUpload({ onUploaded }: DocumentUploadProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<UploadResult | null>(null);

  function acceptFile(selected: File | null | undefined) {
    if (!selected || uploading) return;
    setError(null);

    if (!isPdfFile(selected)) {
      const message = "Vain PDF-tiedostot ovat sallittuja (.pdf)";
      setError(message);
      toast.error("Väärä tiedostotyyppi", message);
      return;
    }
    if (selected.size > MAX_UPLOAD_SIZE_MB * 1024 * 1024) {
      const message = `Tiedosto on liian suuri (enimmäiskoko ${MAX_UPLOAD_SIZE_MB} MB)`;
      setError(message);
      toast.error("Tiedosto on liian suuri", message);
      return;
    }
    setResult(null);
    setFile(selected);
  }

  function handleInputChange(event: ChangeEvent<HTMLInputElement>) {
    acceptFile(event.target.files?.[0]);
  }

  function handleDrop(event: DragEvent<HTMLDivElement>) {
    event.preventDefault();
    setDragActive(false);
    acceptFile(event.dataTransfer.files?.[0]);
  }

  function reset() {
    setFile(null);
    setResult(null);
    setError(null);
    if (inputRef.current) inputRef.current.value = "";
  }

  async function handleUpload() {
    if (!file || uploading) return;

    setUploading(true);
    setError(null);
    try {
      const uploadResult = await documentsApi.upload(file);
      setResult(uploadResult);
      toast.success(
        "Indeksoitu!",
        `${uploadResult.document.filename} — ${uploadResult.chunks_created} chunkkia`,
      );
      onUploaded?.(uploadResult);
      setFile(null);
      if (inputRef.current) inputRef.current.value = "";
    } catch (err) {
      const message = errorMessage(err);
      setError(message);
      toast.error("Lataus epäonnistui", message);
    } finally {
      setUploading(false);
    }
  }

  // Onnistunut indeksointi: näytä tulos ja siirry keskusteluun
  if (result) {
    return (
      <div className="flex flex-col items-center gap-4 rounded-xl border border-emerald-500/40 bg-emerald-50 p-6 text-center dark:bg-emerald-950/40">
        <span className="flex size-12 items-center justify-center rounded-full bg-emerald-500 text-white">
          <FileCheck2 className="size-6" aria-hidden="true" />
        </span>
        <div>
          <p className="font-semibold">Dokumentti indeksoitu!</p>
          <p className="mt-1 text-sm text-muted-foreground">
            {result.document.filename}
            {result.document.page_count != null && <> · {result.document.page_count} sivua</>}
            {" · "}
            {result.chunks_created} chunkkia
          </p>
        </div>
        <div className="flex flex-wrap justify-center gap-2">
          <Link href={`/chat/${result.document.id}`}>
            <span className={buttonVariants()}>
              <MessageSquare aria-hidden="true" /> Aloita keskustelu
            </span>
          </Link>
          <Button variant="outline" onClick={reset}>
            Lataa toinen
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-4">
      <div
        role="button"
        tabIndex={0}
        onClick={() => inputRef.current?.click()}
        onKeyDown={(event) => {
          if (event.key === "Enter" || event.key === " ") {
            event.preventDefault();
            inputRef.current?.click();
          }
        }}
        onDragOver={(event) => {
          event.preventDefault();
          setDragActive(true);
        }}
        onDragLeave={() => setDragActive(false)}
        onDrop={handleDrop}
        className={cn(
          "flex cursor-pointer flex-col items-center justify-center gap-3 rounded-xl border-2 border-dashed p-10 text-center transition-colors",
          dragActive
            ? "border-primary bg-primary/5"
            : "border-border hover:border-primary/50 hover:bg-accent/40",
        )}
      >
        <span className="flex size-12 items-center justify-center rounded-full bg-muted">
          <UploadCloud className="size-6 text-muted-foreground" aria-hidden="true" />
        </span>
        <div>
          <p className="text-sm font-medium">Pudota PDF tähän tai klikkaa valitaksesi</p>
          <p className="mt-1 text-xs text-muted-foreground">
            Enintään {MAX_UPLOAD_SIZE_MB} MB · vain .pdf-tiedostot
          </p>
        </div>
        <input
          ref={inputRef}
          type="file"
          accept="application/pdf,.pdf"
          className="hidden"
          onChange={handleInputChange}
          disabled={uploading}
        />
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertTitle>Latausvirhe</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {file && !uploading && (
        <div className="flex flex-col gap-3 rounded-xl border p-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="min-w-0">
            <p className="truncate text-sm font-medium">{file.name}</p>
            <p className="text-xs text-muted-foreground">{formatBytes(file.size)}</p>
          </div>
          <div className="flex shrink-0 gap-2">
            <Button variant="ghost" size="sm" onClick={reset}>
              Poista
            </Button>
            <Button size="sm" onClick={() => void handleUpload()}>
              <UploadCloud aria-hidden="true" /> Lataa ja indeksoi
            </Button>
          </div>
        </div>
      )}

      {uploading && (
        <div className="rounded-xl border p-4" aria-busy="true" aria-label="Indeksoidaan dokumenttia">
          <div className="flex items-center gap-3">
            <Spinner label="Indeksoidaan" />
            <div className="min-w-0 flex-1">
              <p className="text-sm font-medium">Indeksoidaan…</p>
              <p className="text-xs text-muted-foreground">
                Tekstin purku, chunkkaus ja upotukset voivat kestää hetken.
              </p>
            </div>
          </div>
          <div className="mt-3 h-2 w-full overflow-hidden rounded-full bg-muted">
            <div className="h-full w-1/3 animate-pulse rounded-full bg-primary" />
          </div>
        </div>
      )}
    </div>
  );
}