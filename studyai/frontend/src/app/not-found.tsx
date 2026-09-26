// =============================================================================
// 404-sivu — ei löytynyt
// =============================================================================
import { FileQuestion } from "lucide-react";
import Link from "next/link";

import { buttonVariants } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

export default function NotFound() {
  return (
    <div className="flex min-h-[60vh] items-center justify-center">
      <Card className="w-full max-w-md">
        <CardHeader className="items-center text-center">
          <span className="mb-2 flex size-10 items-center justify-center rounded-lg bg-muted">
            <FileQuestion className="size-5 text-muted-foreground" aria-hidden="true" />
          </span>
          <CardTitle>Sivua ei löytynyt</CardTitle>
          <CardDescription className="text-center">
            Pyytämääsi sivua ei ole olemassa. Se saattaa olla poistettu tai osoite on
            virheellinen.
          </CardDescription>
        </CardHeader>
        <CardContent className="flex flex-wrap justify-center gap-2">
          <Link href="/" className={buttonVariants()}>
            Etusivu
          </Link>
          <Link href="/upload" className={buttonVariants({ variant: "outline" })}>
            Lataa PDF
          </Link>
        </CardContent>
      </Card>
    </div>
  );
}
