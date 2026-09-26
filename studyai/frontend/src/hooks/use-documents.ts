// =============================================================================
// useDocuments: dokumenttilistan haku + poisto (uudelleenlataus)
// =============================================================================
"use client";

import { useCallback, useEffect, useState } from "react";

import { documentsApi } from "@/lib/api";
import { errorMessage } from "@/lib/utils";
import type { DocumentItem } from "@/types";

export interface DocumentsStore {
  documents: DocumentItem[];
  loading: boolean;
  error: string | null;
  /** Hae lista uudelleen (esim. latauksen tai poiston jälkeen). */
  refresh: () => Promise<void>;
  /** Poista dokumentti ja päivitä paikallinen lista. */
  remove: (id: string) => Promise<void>;
}

export function useDocuments(): DocumentsStore {
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      const result = await documentsApi.list();
      setDocuments(result.items);
      setError(null);
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  const remove = useCallback(async (id: string) => {
    await documentsApi.remove(id);
    setDocuments((previous) => previous.filter((document) => document.id !== id));
  }, []);

  return { documents, loading, error, refresh, remove };
}
