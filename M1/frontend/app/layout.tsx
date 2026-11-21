import type { Metadata } from "next";
import "./globals.css";
import { Navbar } from "@/components/layout/Navbar";

export const metadata: Metadata = {
  title: "InternAI | Milestone 2: Intelligent Retrieval & Job-Resume Matching Agent",
  description:
    "Milestone 2 hybrid RAG semantic job discovery, candidate profile matching, and grounded LLM reasoning.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased selection:bg-indigo-500 selection:text-white bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 min-h-screen flex flex-col">
        <Navbar />
        <main className="flex-1 max-w-5xl mx-auto w-full px-4 sm:px-6 py-8">
          {children}
        </main>
      </body>
    </html>
  );
}
