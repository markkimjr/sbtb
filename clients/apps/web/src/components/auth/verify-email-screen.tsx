"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";
import { Mail } from "lucide-react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { createClient } from "@/lib/supabase/browser";

const COOLDOWN_SECONDS = 30;

export function VerifyEmailScreen() {
  const params = useSearchParams();
  const email = params.get("email");
  const [cooldown, setCooldown] = useState(0);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (cooldown <= 0) return;
    const id = setInterval(() => setCooldown((c) => Math.max(0, c - 1)), 1000);
    return () => clearInterval(id);
  }, [cooldown]);

  if (!email) {
    return (
      <div className="space-y-4 text-center">
        <p className="text-sm opacity-70">
          We can't find which email you're verifying.
        </p>
        <Link href="/signup" className="underline text-sm">
          Sign up first
        </Link>
      </div>
    );
  }

  async function onResend() {
    if (!email) return;
    setSubmitting(true);
    const supabase = createClient();
    const { error } = await supabase.auth.resend({ type: "signup", email });
    setSubmitting(false);

    if (error) {
      toast.error(error.message);
      return;
    }
    toast.success("Verification email sent.");
    setCooldown(COOLDOWN_SECONDS);
  }

  const buttonLabel =
    cooldown > 0 ? `Resend in ${cooldown}s` : submitting ? "Sending…" : "Resend email";

  return (
    <div className="space-y-6 text-center">
      <div className="mx-auto w-12 h-12 grid place-items-center rounded-xl bg-[var(--color-sand)]">
        <Mail className="w-5 h-5" strokeWidth={1.75} />
      </div>
      <header className="space-y-2">
        <h1 className="font-display italic text-3xl">Check your inbox.</h1>
        <p className="text-sm opacity-70">
          We sent a confirmation link to{" "}
          <span className="font-medium">{email}</span>. Click it to finish setting
          up your account.
        </p>
      </header>
      <p className="text-xs opacity-60">Didn't get it? Check your spam folder.</p>
      <Button
        type="button"
        variant="outline"
        className="w-full"
        onClick={onResend}
        disabled={cooldown > 0 || submitting}
      >
        {buttonLabel}
      </Button>
    </div>
  );
}
