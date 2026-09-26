// =============================================================================
// Toaster — renderöi toast-ilmoitukset (asenna layoutiin)
// =============================================================================
"use client";

import { AlertCircle, CheckCircle2, Info, X } from "lucide-react";

import { dismissToast, useToasts, type ToastVariant } from "@/hooks/use-toast";
import { cn } from "@/lib/utils";

const ICONS: Record<ToastVariant, typeof Info> = {
  default: Info,
  success: CheckCircle2,
  error: AlertCircle,
};

const ICON_COLORS: Record<ToastVariant, string> = {
  default: "text-primary",
  success: "text-emerald-500",
  error: "text-destructive",
};

export function Toaster() {
  const toasts = useToasts();
  if (toasts.length === 0) return null;

  return (
    <div
      aria-live="polite"
      className="pointer-events-none fixed inset-x-4 bottom-4 z-50 flex flex-col items-end gap-2 sm:inset-x-auto sm:right-4 sm:w-full sm:max-w-sm"
    >
      {toasts.map((item) => {
        const Icon = ICONS[item.variant];
        return (
          <div
            key={item.id}
            role="status"
            className={cn(
              "pointer-events-auto flex w-full items-start gap-3 rounded-lg border bg-background p-4 shadow-lg",
              "animate-in fade-in slide-in-from-bottom-2 duration-300",
            )}
          >
            <Icon className={cn("mt-0.5 size-5 shrink-0", ICON_COLORS[item.variant])} />
            <div className="min-w-0 flex-1">
              <p className="text-sm font-semibold">{item.title}</p>
              {item.description && (
                <p className="mt-1 text-xs text-muted-foreground">{item.description}</p>
              )}
            </div>
            <button
              type="button"
              onClick={() => dismissToast(item.id)}
              className="rounded-md p-1 text-muted-foreground transition-colors hover:text-foreground"
              aria-label="Sulje ilmoitus"
            >
              <X className="size-4" />
            </button>
          </div>
        );
      })}
    </div>
  );
}
