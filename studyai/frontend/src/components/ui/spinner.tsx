// =============================================================================
// shadcn/ui — Spinner (latausindikaattori)
// =============================================================================
import { Loader2 } from "lucide-react";

import { cn } from "@/lib/utils";

interface SpinnerProps {
  className?: string;
  /** Saatavilla lukevien ruudunlukijoiden kuvaus (oletuksena "Ladataan"). */
  label?: string;
}

function Spinner({ className, label = "Ladataan" }: SpinnerProps) {
  return (
    <span role="status" aria-label={label} className="inline-flex items-center">
      <Loader2 className={cn("h-4 w-4 animate-spin", className)} aria-hidden="true" />
      <span className="sr-only">{label}</span>
    </span>
  );
}

export { Spinner };
