// =============================================================================
// StudyAI — dokumentin latauskomponentti (runko)
// Varsinainen toteutus lisätään seuraavassa vaiheessa.
// =============================================================================
"use client";

import { useState } from "react";

import { documentsApi } from "@/lib/api";
import type { UploadResult } from "@/types";

export function DocumentUpload() {
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState<UploadResult | null>(null);

  async function handleFileChange(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;
    setUploading(true);
    try {
      // Varsinainen kutsu; backend vastaa 501 toistaiseksi.
      const res = await documentsApi.upload(file);
      setResult(res);
    } finally {
      setUploading(false);
    }
  }

  return (
    <div className="rounded-lg border border-dashed p-6 text-center">
      <input
        type="file"
        accept="application/pdf"
        onChange={handleFileChange}
        disabled={uploading}
      />
      {result && <p className="mt-2 text-sm">{result.message}</p>}
    </div>
  );
}