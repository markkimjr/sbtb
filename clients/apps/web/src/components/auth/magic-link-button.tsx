"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { z } from "zod";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { createClient } from "@/lib/supabase/browser";

const COOLDOWN_SECONDS = 30;

const schema = z.object({
  email: z.string().email("Enter a valid email"),
});

type FormValues = z.infer<typeof schema>;

export function MagicLinkButton() {
  const [cooldown, setCooldown] = useState(0);
  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { email: "" },
  });

  useEffect(() => {
    if (cooldown <= 0) return;
    const id = setInterval(() => setCooldown((c) => Math.max(0, c - 1)), 1000);
    return () => clearInterval(id);
  }, [cooldown]);

  async function onSubmit({ email }: FormValues) {
    const supabase = createClient();
    const { error } = await supabase.auth.signInWithOtp({
      email,
      options: {
        emailRedirectTo: `${window.location.origin}/auth/callback?next=/fighters`,
      },
    });

    if (error) {
      toast.error(error.message);
      return;
    }

    toast.success("Sign-in link sent if an account exists for that email.");
    setCooldown(COOLDOWN_SECONDS);
  }

  const disabled = cooldown > 0;
  const label = cooldown > 0 ? `Resend in ${cooldown}s` : "Send me a sign-in link instead";

  return (
    <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-3" noValidate>
      <div className="space-y-1.5">
        <Label htmlFor="magic-link-email">Email</Label>
        <Input
          id="magic-link-email"
          type="email"
          autoComplete="email"
          {...form.register("email")}
        />
        {form.formState.errors.email && (
          <p className="text-xs text-[var(--color-persimmon)]">
            {form.formState.errors.email.message}
          </p>
        )}
      </div>
      <Button type="submit" variant="ghost" className="w-full text-sm" disabled={disabled}>
        {label}
      </Button>
    </form>
  );
}
