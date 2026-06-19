"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { z } from "zod";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { createClient } from "@/lib/supabase/browser";

const schema = z
  .object({
    password: z.string().min(8, "At least 8 characters"),
    confirm: z.string(),
  })
  .refine((d) => d.password === d.confirm, {
    path: ["confirm"],
    message: "Passwords don't match",
  });

type FormValues = z.infer<typeof schema>;

export function SetPasswordForm({ onPasswordSet }: { onPasswordSet: () => void }) {
  const [submitting, setSubmitting] = useState(false);
  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { password: "", confirm: "" },
  });

  async function onSubmit({ password }: FormValues) {
    setSubmitting(true);
    const supabase = createClient();
    const { error } = await supabase.auth.updateUser({ password });
    setSubmitting(false);

    if (error) {
      toast.error(error.message);
      return;
    }
    toast.success("Password set.");
    onPasswordSet();
  }

  return (
    <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-3" noValidate>
      <div className="space-y-1.5">
        <Label htmlFor="profile-password">Password</Label>
        <Input
          id="profile-password"
          type="password"
          autoComplete="new-password"
          {...form.register("password")}
        />
        {form.formState.errors.password && (
          <p className="text-xs text-[var(--color-persimmon)]">
            {form.formState.errors.password.message}
          </p>
        )}
      </div>
      <div className="space-y-1.5">
        <Label htmlFor="profile-password-confirm">Confirm</Label>
        <Input
          id="profile-password-confirm"
          type="password"
          autoComplete="new-password"
          {...form.register("confirm")}
        />
        {form.formState.errors.confirm && (
          <p className="text-xs text-[var(--color-persimmon)]">
            {form.formState.errors.confirm.message}
          </p>
        )}
      </div>
      <Button type="submit" disabled={submitting}>
        {submitting ? "Saving…" : "Save password"}
      </Button>
    </form>
  );
}
