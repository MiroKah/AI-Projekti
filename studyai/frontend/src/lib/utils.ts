import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

/**
 * Yhdistää Tailwind-luokat turvallisesti (shadcn/ui:n käyttämä apuri).
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/** Muotoilee tavukoon luettavaan muotoon. */
export function formatBytes(bytes: number | null | undefined): string {
  if (!bytes || bytes <= 0) return "–";
  const units = ["B", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${units[i]}`;
}