"use client";

import { Mail } from "lucide-react";
import { useSearchParams } from "next/navigation";

export function VerifyEmailScreen() {
  const params = useSearchParams();
  const email = params.get("email");

  return (
    <div className="space-y-6 text-center">
      <div className="mx-auto w-12 h-12 grid place-items-center rounded-xl bg-[var(--color-sand)]">
        <Mail className="w-5 h-5" strokeWidth={1.75} />
      </div>
      <header className="space-y-2">
        <h1 className="font-display italic text-3xl">Check your inbox.</h1>
        <p className="text-sm opacity-70">
          We sent a confirmation link to{" "}
          <span className="font-medium">{email ?? "your email"}</span>. Click it
          to finish setting up your account.
        </p>
      </header>
      <p className="text-xs opacity-60">Didn&apos;t get it? Check your spam folder.</p>
    </div>
  );
}
