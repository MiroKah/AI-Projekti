// =============================================================================
// StudyAI — juuriasettelu (layout): teema, navigaatio, toastit
// =============================================================================
import type { Metadata } from "next";
import type { ReactNode } from "react";

import { Sidebar } from "@/components/layout/sidebar";
import { ThemeProvider } from "@/components/layout/theme-provider";
import { Toaster } from "@/components/ui/toaster";

import "./globals.css";

export const metadata: Metadata = {
  title: {
    default: "StudyAI",
    template: "%s | StudyAI",
  },
  description:
    "Keskustele omien PDF-dokumenttien kanssa — vastaukset perustuvat vain ladattuun materiaaliin.",
};

// Estetään teeman välkkyminen ennen hydrataatiota (localStorage / järjestelmäteema)
const THEME_SCRIPT = `(function(){try{var t=localStorage.getItem("studyai-theme");if(t!=="light"&&t!=="dark"){t=window.matchMedia("(prefers-color-scheme: dark)").matches?"dark":"light";}if(t==="dark"){document.documentElement.classList.add("dark");}}catch(e){}})();`;

export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <html lang="fi" suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: THEME_SCRIPT }} />
      </head>
      <body className="min-h-screen bg-background text-foreground antialiased">
        <ThemeProvider>
          <Sidebar />
          {/* Mobiilissa tilaa yläpalkille (h-14), desktopissa sidebar-vuoroinen tila */}
          <div className="pt-14 lg:pl-64 lg:pt-0">
            <div className="mx-auto w-full max-w-6xl px-4 py-6 sm:px-6 lg:px-8 lg:py-8">
              {children}
            </div>
          </div>
          <Toaster />
        </ThemeProvider>
      </body>
    </html>
  );
}
