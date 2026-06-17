"use client";

import { BookmarkButton } from "@/components/fighters/bookmark-button";
import { FighterCarousel } from "@/components/fighters/fighter-carousel";
import { FighterSearchBar } from "@/components/fighters/fighter-search-bar";
import { FirstBookmarkModal } from "@/components/fighters/first-bookmark-modal";
import { useFeaturedFighters } from "@/hooks/use-featured-fighters";
import { useToggleBookmark } from "@/hooks/use-toggle-bookmark";
import { useUser } from "@/hooks/use-user";
import { useEffect, useState } from "react";

export default function FightersPage() {
  const [, setQuery] = useState("");
  const { data: fighters = [] } = useFeaturedFighters();

  const { data: user } = useUser();
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
        <FighterSearchBar onChange={setQuery} />
      </div>

      <FighterCarousel
        fighters={fighters}
        renderBookmark={(f) => <BookmarkButton fighterId={f.id} fighterName={f.name} />}
      />

      <FirstBookmarkModal />
    </div>
  );
}
