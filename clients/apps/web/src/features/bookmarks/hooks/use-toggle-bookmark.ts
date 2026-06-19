"use client";

import { useBookmarkStore } from "@/features/bookmarks/store/bookmarks";
import { useCurrentUser } from "@/hooks/use-current-user";
import { usePathname, useRouter } from "next/navigation";
import { toast } from "sonner";

export function useToggleBookmark() {
  const { supabaseUser: user } = useCurrentUser();
  const router = useRouter();
  const pathname = usePathname();
  const { bookmarks, hasSeenIntro, addBookmark, removeBookmark, openFirstBookmark } =
    useBookmarkStore();

  function toggle(fighterId: string, fighterName?: string) {
    if (!user) {
      const next = encodeURIComponent(pathname);
      router.push(`/signup?next=${next}&fighter=${fighterId}`);
      return;
    }

    const isSaved = bookmarks.has(fighterId);

    if (isSaved) {
      removeBookmark(fighterId);
      toast(`Removed ${fighterName ?? "fighter"}`);
      return;
    }

    if (!hasSeenIntro) {
      openFirstBookmark(fighterId);
      return;
    }

    addBookmark(fighterId);
    toast(`Saved ${fighterName ?? "fighter"}`);
  }

  return {
    toggle,
    isBookmarked: (id: string) => bookmarks.has(id),
  };
}
