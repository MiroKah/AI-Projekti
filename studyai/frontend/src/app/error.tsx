// =============================================================================
// Globaali virhesivu (Next.js error boundary) — renderöityyn virheeseen
// =============================================================================
"use client";

import { AlertTriangle, RefreshCcw } from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

export default function Error({ error, reset }: { error: Error & { digest?: string }; reset: () => void }) {
  return (
    <div className="flex min-h-[60vh] items-center justify-center">
      <Card className="w-full max-w-md">
        <CardHeader>
          <span className="mb-2 flex size-10 items-center justify-center rounded-lg bg-destructive/10 text-destructive">
            <AlertTriangle className="size-5" aria-hidden="true" />
          </span>
          <CardTitle>Jotain meni pieleen</CardTitle>
          <CardDescription>
            {error.message || "Odottamaton virhe. Yritä uudelleen hetken päästä."}
            {error.digest && <span className="mt-1 block text-xs">Tunniste: {error.digest}</span>}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Button onClick={reset}>
            <RefreshCcw aria-hidden="true" /> Yritä uudelleen
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
