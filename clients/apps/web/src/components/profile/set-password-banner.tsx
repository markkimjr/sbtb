"use client";

import { useState } from "react";

import { SetPasswordForm } from "@/components/profile/set-password-form";
import { Button } from "@/components/ui/button";
import { useCurrentUser } from "@/hooks/use-current-user";

export function SetPasswordBanner() {
  const { supabaseUser } = useCurrentUser();
  const [expanded, setExpanded] = useState(false);
  const [done, setDone] = useState(false);

  if (done || !supabaseUser) return null;

  const identities = supabaseUser.identities ?? [];
  const hasEmailIdentity = identities.some((i) => i.provider === "email");
  if (hasEmailIdentity) return null;

  return (
    <div className="rounded-xl border border-[var(--color-sand)] p-4 space-y-3">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="font-display italic text-lg">Set a password</p>
          <p className="text-sm opacity-70">
            You signed up with a social provider. Set a password to log in faster
            next time.
          </p>
        </div>
        {!expanded && (
          <Button
            type="button"
            variant="outline"
            onClick={() => setExpanded(true)}
          >
            Set a password
          </Button>
        )}
      </div>
      {expanded && <SetPasswordForm onPasswordSet={() => setDone(true)} />}
    </div>
  );
}
