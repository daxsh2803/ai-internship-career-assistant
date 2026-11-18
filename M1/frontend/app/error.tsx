"use client";

import { useEffect } from "react";
import { Button } from "@/components/ui/Button";

export default function ErrorBoundary({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error("Application error:", error);
  }, [error]);

  return (
    <div className="flex flex-col items-center justify-center min-h-[50vh] text-center space-y-4 p-6">
      <h2 className="text-xl font-bold text-slate-900 dark:text-white">
        Something went wrong
      </h2>
      <p className="text-sm text-slate-500 max-w-md">
        An unexpected error occurred while rendering this page.
      </p>
      <Button variant="primary" size="sm" onClick={() => reset()}>
        Try Again
      </Button>
    </div>
  );
}
