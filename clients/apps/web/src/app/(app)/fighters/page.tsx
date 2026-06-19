"use client";

import { useToggleBookmark } from "@/features/bookmarks/hooks/use-toggle-bookmark";
import { BookmarkButton } from "@/features/fighters/components/bookmark-button";
import { FighterCarousel } from "@/features/fighters/components/fighter-carousel";
import { FighterSearchBar } from "@/features/fighters/components/fighter-search-bar";
import { FirstBookmarkModal } from "@/features/fighters/components/first-bookmark-modal";
import { useFeaturedFighters } from "@/features/fighters/hooks/use-featured-fighters";
import { useCurrentUser } from "@/hooks/use-current-user";
import { useEffect } from "react";

export default function FightersPage() {
  const { data: fighters = [] } = useFeaturedFighters();

  const { supabaseUser: user } = useCurrentUser();
  const { toggle, isBookmarked } = useToggleBookmark();

  // Honor ?fighter= from a post-signup redirect — auto-bookmark on sign-in.
  useEffect(() => {
    if (!user) return;
    const params = new URLSearchParams(window.location.search);
    const fighterId = params.get("fighter");
    if (!fighterId) return;
    if (isBookmarked(fighterId)) return;
    const fighter = fighters.find((f) => f.id === fighterId);
    if (fighter) toggle(fighter.id, fighter.name);
    params.delete("fighter");
    const search = params.toString();
    const url = window.location.pathname + (search ? `?${search}` : "");
    window.history.replaceState({}, "", url);
  }, [user, fighters, toggle, isBookmarked]);

  return (
    <div className="flex-1 flex flex-col">
      <div className="px-9 pt-7 pb-3 flex items-center justify-between gap-6">
        <div className="flex flex-col gap-1">
          <h1 className="font-display italic text-2xl leading-tight tracking-tight">
            Pick your <span className="not-italic text-[var(--color-persimmon)]">fighters.</span>
          </h1>
          <p className="text-[13px] opacity-70">
            We ring the <span className="font-display italic text-[14px]">bell</span> when they
            fight next.
          </p>
        </div>
        <FighterSearchBar />
      </div>

      <FighterCarousel
        fighters={fighters}
        renderBookmark={(f) => <BookmarkButton fighterId={f.id} fighterName={f.name} />}
      />

      <FirstBookmarkModal />
    </div>
  );
}
