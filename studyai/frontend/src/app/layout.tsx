// =============================================================================
// StudyAI — juuriasettelu (layout)
// =============================================================================
import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "StudyAI",
  description: "Keskustele PDF-dokumenttien kanssa (RAG).",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="fi">
      <body className="min-h-screen bg-background text-foreground antialiased">
        {children}
      </body>
    </html>
  );
}