"use client";

import { useToggleBookmark } from "@/features/bookmarks/hooks/use-toggle-bookmark";
import { useBookmarkStore } from "@/features/bookmarks/store/bookmarks";
import { useFeaturedFighters } from "@/features/fighters/hooks/use-featured-fighters";
import { Bookmark } from "lucide-react";

export function BookmarkedFightersGrid() {
  const bookmarks = useBookmarkStore((s) => s.bookmarks);
  const { toggle } = useToggleBookmark();
  const { data: fighters = [] } = useFeaturedFighters();

  const saved = fighters.filter((f) => bookmarks.has(f.id));

  if (saved.length === 0) {
    return (
      <section className="space-y-4">
        <div className="space-y-1">
          <h2 className="font-display italic text-2xl">Your bookmarked fighters</h2>
          <p className="text-sm opacity-70">
            You haven&apos;t saved any fighters yet — head back to the carousel and tap the bookmark
            icon.
          </p>
        </div>
      </section>
    );
  }

  return (
    <section className="space-y-4">
      <div className="space-y-1">
        <h2 className="font-display italic text-2xl">Your bookmarked fighters</h2>
        <p className="text-sm opacity-70">Tap the bookmark to remove.</p>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
        {saved.map((f) => (
          <div
            key={f.id}
            className="bg-[color-mix(in_srgb,white_30%,transparent)] border border-[var(--color-sand)] rounded-2xl overflow-hidden"
          >
            <div
              className="aspect-square w-full"
              style={{
                background: "linear-gradient(135deg, #c19c7a 0%, #836040 50%, #3a2715 100%)",
              }}
            />
            <div className="p-3 flex items-center justify-between gap-2">
              <div className="min-w-0">
                <div className="font-display italic text-base leading-tight truncate">{f.name}</div>
              </div>
              <button
                type="button"
                aria-label={`Remove ${f.name}`}
                onClick={() => toggle(f.id, f.name)}
                className="w-8 h-8 rounded-lg bg-[var(--color-persimmon)] grid place-items-center shrink-0"
              >
                <Bookmark
                  className="w-4 h-4"
                  strokeWidth={1.5}
                  fill="var(--color-parchment)"
                  stroke="var(--color-parchment)"
                />
              </button>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
