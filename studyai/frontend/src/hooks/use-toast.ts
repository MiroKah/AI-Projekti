// =============================================================================
// Toast-ilmoitukset: moduulipohjainen store + hook (tarvitsee Toasterin layoutiin)
// =============================================================================
"use client";

import { useSyncExternalStore } from "react";

export type ToastVariant = "default" | "success" | "error";

export interface ToastItem {
  id: number;
  title: string;
  description?: string;
  variant: ToastVariant;
}

type ToastInput = Omit<ToastItem, "id">;

interface ToastFn {
  (input: ToastInput): number;
  success(title: string, description?: string): number;
  error(title: string, description?: string): number;
}

let toasts: ToastItem[] = [];
let nextId = 0;
const listeners = new Set<() => void>();
const EMPTY: ToastItem[] = [];

function emit(): void {
  listeners.forEach((listener) => listener());
}

export function dismissToast(id: number): void {
  toasts = toasts.filter((toastItem) => toastItem.id !== id);
  emit();
}

function showToast(input: ToastInput): number {
  const id = ++nextId;
  toasts = [...toasts, { id, ...input }];
  emit();
  setTimeout(() => dismissToast(id), 5000);
  return id;
}

/** Näyttää toast-ilmoituksen: toast({ title, description, variant }). */
export const toast: ToastFn = Object.assign(showToast, {
  success(title: string, description?: string): number {
    return showToast({ title, description, variant: "success" });
  },
  error(title: string, description?: string): number {
    return showToast({ title, description, variant: "error" });
  },
});

/** Palauttaa aktiiviset tostit (käytä komponenteissa). */
export function useToasts(): ToastItem[] {
  return useSyncExternalStore(
    (callback) => {
      listeners.add(callback);
      return () => listeners.delete(callback);
    },
    () => toasts,
    () => EMPTY,
  );
}
