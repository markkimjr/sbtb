"use client";

import { Button } from "@/components/ui/button";
import { createClient } from "@/lib/supabase/browser";
import { useSearchParams } from "next/navigation";
import { useState } from "react";
import { toast } from "sonner";

export function GoogleOAuthButton({ label }: { label: string }) {
  const params = useSearchParams();
  const [submitting, setSubmitting] = useState(false);

  async function onClick() {
    setSubmitting(true);
    const supabase = createClient();
    const next = params.get("next") ?? "/fighters";
    const fighter = params.get("fighter");

    const callbackParams = new URLSearchParams({ next });
    if (fighter) callbackParams.set("fighter", fighter);

    const { error } = await supabase.auth.signInWithOAuth({
      provider: "google",
      options: {
        redirectTo: `${window.location.origin}/auth/callback?${callbackParams.toString()}`,
      },
    });

    if (error) {
      setSubmitting(false);
      toast.error(error.message);
    }
  }

  return (
    <Button
      type="button"
      variant="outline"
      className="w-full"
      onClick={onClick}
      disabled={submitting}
    >
      <svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true" className="mr-2">
        <path
          fill="#EA4335"
          d="M12 11v3.4h5.4c-.2 1.4-1.7 4.1-5.4 4.1-3.3 0-6-2.7-6-6s2.7-6 6-6c1.9 0 3.1.8 3.8 1.5l2.6-2.5C16.7 4 14.6 3 12 3 6.9 3 2.8 7.1 2.8 12.5S6.9 22 12 22c6 0 9.9-4.2 9.9-10.1 0-.7-.1-1.2-.2-1.9H12z"
        />
      </svg>
      {label}
    </Button>
  );
}
