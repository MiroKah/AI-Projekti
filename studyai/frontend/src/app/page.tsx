// =============================================================================
// Etusivu / Dashboard: tilastot + dokumenttilista + nopeat toiminnot
// =============================================================================
"use client";

import Link from "next/link";
import { BookOpen, CheckCircle2, FileText, HardDrive, UploadCloud } from "lucide-react";

import { DocumentList } from "@/components/documents/document-list";
import { Button, buttonVariants } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useDocuments } from "@/hooks/use-documents";
import { formatBytes } from "@/lib/utils";

export default function DashboardPage() {
  const { documents, loading, error, refresh, remove } = useDocuments();

  const readyCount = documents.filter((document) => document.status === "ready").length;
  const totalPages = documents.reduce((sum, document) => sum + (document.page_count ?? 0), 0);
  const totalSize = documents.reduce((sum, document) => sum + (document.size_bytes ?? 0), 0);

  const stats = [
    { label: "Dokumentteja", value: String(documents.length), icon: FileText },
    { label: "Valmiita keskusteluun", value: String(readyCount), icon: CheckCircle2 },
    { label: "Sivua yhteensä", value: String(totalPages), icon: BookOpen },
    { label: "Kokonaiskoko", value: formatBytes(totalSize), icon: HardDrive },
  ];

  return (
    <div className="space-y-6">
      {/* Tervetuloa + nopea toiminto */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Etusivu</h1>
          <p className="mt-1 max-w-xl text-sm text-muted-foreground">
            Lataa oppimateriaalisi ja keskustele sen kanssa — vastaukset perustuvat vain omiin
            dokumentteihisi.
          </p>
        </div>
        <Link href="/upload" className={buttonVariants({ size: "lg" })}>
          <UploadCloud aria-hidden="true" /> Lataa uusi PDF
        </Link>
      </div>

      {/* Tilastokortit */}
      <div className="grid grid-cols-2 gap-3 xl:grid-cols-4">
        {stats.map((stat) => (
          <Card key={stat.label}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                {stat.label}
              </CardTitle>
              <stat.icon className="size-4 text-muted-foreground" aria-hidden="true" />
            </CardHeader>
            <CardContent>
              {loading ? (
                <Skeleton className="h-7 w-16" />
              ) : (
                <p className="text-2xl font-bold tabular-nums">{stat.value}</p>
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Dokumenttilista */}
      <section className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">Dokumentit</h2>
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
