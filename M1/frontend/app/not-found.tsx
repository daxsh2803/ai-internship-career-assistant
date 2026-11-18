"use client";

import Link from "next/link";

export default function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[50vh] text-center space-y-4">
      <h2 className="text-2xl font-bold text-slate-800 dark:text-slate-200">Page Not Found</h2>
      <p className="text-sm text-slate-500">The requested resource could not be found.</p>
      <Link
        href="/"
        className="px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700 transition-colors"
      >
        Return to Home
      </Link>
    </div>
  );
}
