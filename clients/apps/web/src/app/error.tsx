"use client";

import { Button } from "@/components/ui/button";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="min-h-screen grid place-items-center px-6">
      <div className="max-w-md text-center space-y-4">
        <h1 className="font-display italic text-4xl">Something went sideways.</h1>
        <p className="text-sm opacity-75">{error.message || "An unexpected error occurred."}</p>
        <Button onClick={() => reset()}>Try again</Button>
      </div>
    </div>
  );
}
