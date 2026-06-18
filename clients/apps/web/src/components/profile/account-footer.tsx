"use client";

import { Button } from "@/components/ui/button";
import { useCurrentUser } from "@/hooks/use-current-user";
import { createClient } from "@/lib/supabase/browser";
import { useRouter } from "next/navigation";
import { toast } from "sonner";

export function AccountFooter() {
  const { supabaseUser: user } = useCurrentUser();
  const router = useRouter();

  async function onSignOut() {
    const supabase = createClient();
    const { error } = await supabase.auth.signOut();
    if (error) {
      toast.error(error.message);
      return;
    }
    router.push("/fighters");
    router.refresh();
  }

  return (
    <section className="flex items-center justify-between border-t border-[var(--color-sand)] pt-6">
      <p className="text-sm opacity-70">
        Signed in as <span className="font-medium">{user?.email ?? "…"}</span>
      </p>
      <Button variant="outline" size="sm" onClick={onSignOut}>
        Sign out
      </Button>
    </section>
  );
}
