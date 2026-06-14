"use client";

import { usePathname, useRouter } from "next/navigation";
import { toast } from "sonner";
import { useUser } from "@/hooks/use-user";
import { useModalStore } from "@/store/modal";

export function useToggleBookmark() {
  const { data: user } = useUser();
  const router = useRouter();
  const pathname = usePathname();
  const { bookmarks, hasSeenIntro, addBookmark, removeBookmark, openFirstBookmark } =
    useModalStore();

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
