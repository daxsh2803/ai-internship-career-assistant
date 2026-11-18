"use client";

import React from "react";
import Link from "next/link";
import { Sparkles } from "lucide-react";
import { Badge } from "@/components/ui/Badge";

export const Navbar: React.FC = () => {
  return (
    <header className="sticky top-0 z-40 w-full bg-white/90 dark:bg-slate-900/90 backdrop-blur-md border-b border-slate-200 dark:border-slate-800">
      <div className="max-w-5xl mx-auto flex h-16 items-center justify-between px-4 sm:px-6">

        <Link href="/" className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center text-white shadow-sm">
            <Sparkles className="w-4 h-4" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="font-bold text-slate-900 dark:text-white text-base tracking-tight">
              InternAI
            </span>
            <span className="text-xs text-slate-500 dark:text-slate-400 font-medium">
              Springboard
            </span>
          </div>
          <Badge variant="indigo" size="sm" className="ml-1 font-medium">
            Milestone 1
          </Badge>
        </Link>
      </div>
    </header>
  );
};
