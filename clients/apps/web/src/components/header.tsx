"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useUser } from "@/hooks/use-user";
import { createClient } from "@/lib/supabase/browser";

export function Header() {
  const router = useRouter();
  const { data: user, isLoading } = useUser();

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

  const initial = user?.email?.[0]?.toUpperCase() ?? "?";

  return (
    <header className="flex items-center justify-between px-9 py-4 border-b border-[var(--color-sand)]">
      <Link href="/fighters" className="ink-stamp font-display italic text-xl px-2">
        saved by the bell
      </Link>

      <nav className="flex items-center gap-4 text-sm">
        {isLoading ? (
          <div className="w-20 h-8" />
        ) : user ? (
          <DropdownMenu>
            <DropdownMenuTrigger aria-label="Profile menu" className="rounded-full">
              <Avatar className="h-8 w-8">
                <AvatarFallback className="bg-[var(--color-sand)] text-[var(--color-ink)] text-sm">
                  {initial}
                </AvatarFallback>
              </Avatar>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-44">
              <DropdownMenuItem>
                <Link href="/profile" className="w-full">Profile</Link>
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={onSignOut}>Sign out</DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        ) : (
          <>
            <Link href="/login" className="opacity-75 hover:opacity-100">
              Log in
            </Link>
            <Link href="/signup">
              <Button size="sm">Sign up</Button>
            </Link>
          </>
        )}
      </nav>
    </header>
  );
}
