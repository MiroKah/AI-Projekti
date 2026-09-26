// =============================================================================
// Sidebar: navigaatio (Etusivu, Lataa PDF, Keskustelu) + teeman vaihto
// Desktop: kiinteä sivupalkki. Mobiili: yläpalkki + vetopohja (drawer).
// =============================================================================
"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  GraduationCap,
  LayoutDashboard,
  MessagesSquare,
  Menu,
  Upload,
  X,
  type LucideIcon,
} from "lucide-react";

import { ThemeToggle } from "@/components/layout/theme-toggle";
import { cn } from "@/lib/utils";

interface NavItem {
  href: string;
  label: string;
  icon: LucideIcon;
}

const NAV_ITEMS: NavItem[] = [
  { href: "/", label: "Etusivu", icon: LayoutDashboard },
  { href: "/upload", label: "Lataa PDF", icon: Upload },
  { href: "/chat", label: "Keskustelu", icon: MessagesSquare },
];

function Brand() {
  return (
    <Link href="/" className="flex items-center gap-2.5">
      <span className="flex size-9 items-center justify-center rounded-lg bg-primary text-primary-foreground">
        <GraduationCap className="size-5" aria-hidden="true" />
      </span>
      <span>
        <span className="block text-base font-bold leading-tight">StudyAI</span>
        <span className="block text-xs text-muted-foreground">opiskelu-assistentti</span>
      </span>
    </Link>
  );
}

function NavLinks({ onNavigate }: { onNavigate?: () => void }) {
  const pathname = usePathname();

  return (
    <nav className="flex flex-1 flex-col gap-1" aria-label="Päänavigaatio">
      {NAV_ITEMS.map((item) => {
        const active =
          pathname === item.href || (item.href !== "/" && pathname.startsWith(item.href));
        return (
          <Link
            key={item.href}
            href={item.href}
            onClick={onNavigate}
            className={cn(
              "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
              active
                ? "bg-accent text-accent-foreground"
                : "text-muted-foreground hover:bg-accent/60 hover:text-foreground",
            )}
            aria-current={active ? "page" : undefined}
          >
            <item.icon className="size-5 shrink-0" aria-hidden="true" />
            {item.label}
          </Link>
        );
      })}
    </nav>
  );
}

function SidebarFooter() {
  return (
    <div className="flex items-center justify-between border-t pt-3">
      <p className="text-xs text-muted-foreground">Vain ladattu materiaali<br />pohjana vastauksille.</p>
      <ThemeToggle />
    </div>
  );
}

export function Sidebar() {
  const [open, setOpen] = useState(false);
  const pathname = usePathname();

  // Sulje mobiilivalikko reitin vaihtuessa + Escape-näppäin sulkee sen
  useEffect(() => {
    setOpen(false);
  }, [pathname]);

  useEffect(() => {
    if (!open) return;
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") setOpen(false);
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [open]);

  return (
    <>
      {/* Desktop: kiinteä sivupalkki */}
      <aside className="fixed inset-y-0 left-0 z-30 hidden w-64 flex-col gap-6 border-r bg-card p-4 lg:flex">
        <Brand />
        <NavLinks />
        <SidebarFooter />
      </aside>

      {/* Mobiili: yläpalkki */}
      <header className="fixed inset-x-0 top-0 z-30 flex h-14 items-center justify-between border-b bg-background/95 px-4 backdrop-blur lg:hidden">
        <button
          type="button"
          className="rounded-md p-2 text-muted-foreground hover:text-foreground"
          onClick={() => setOpen((value) => !value)}
          aria-label={open ? "Sulje valikko" : "Avaa valikko"}
          aria-expanded={open}
        >
          {open ? <X className="size-5" /> : <Menu className="size-5" />}
        </button>
        <Brand />
        <ThemeToggle />
      </header>

      {/* Mobiili: vetopohja */}
      {open && (
        <div className="fixed inset-0 z-40 lg:hidden">
          <button
            type="button"
            className="absolute inset-0 bg-black/50"
            onClick={() => setOpen(false)}
            aria-label="Sulje valikko"
          />
          <div className="absolute inset-y-0 left-0 flex w-72 flex-col gap-6 border-r bg-card p-4 shadow-xl">
            <div className="flex items-center justify-between">
              <Brand />
              <button
                type="button"
                className="rounded-md p-2 text-muted-foreground hover:text-foreground"
                onClick={() => setOpen(false)}
                aria-label="Sulje valikko"
              >
                <X className="size-5" />
              </button>
            </div>
            <NavLinks onNavigate={() => setOpen(false)} />
            <SidebarFooter />
          </div>
        </div>
      )}
    </>
  );
}
