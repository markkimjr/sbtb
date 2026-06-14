"use client";

import { ChevronLeft, ChevronRight } from "lucide-react";
import { type ReactNode, useEffect } from "react";
import { useCarouselStore } from "@/store/carousel";
import type { Fighter } from "@/types/fighter";
import { FighterCard } from "./fighter-card";

type FighterCarouselProps = {
  fighters: Fighter[];
  renderBookmark: (fighter: Fighter) => ReactNode;
};

export function FighterCarousel({ fighters, renderBookmark }: FighterCarouselProps) {
  const { index, setTotal, next, prev } = useCarouselStore();

  useEffect(() => {
    setTotal(fighters.length);
  }, [fighters.length, setTotal]);

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (e.key === "ArrowLeft") prev();
      if (e.key === "ArrowRight") next();
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [next, prev]);

  if (fighters.length === 0) {
    return (
      <div className="flex-1 grid place-items-center">
        <p className="text-sm opacity-60">No fighters match your search.</p>
      </div>
    );
  }

  const focus = fighters[index];
  const prevFighter = fighters[(index - 1 + fighters.length) % fighters.length];
  const nextFighter = fighters[(index + 1) % fighters.length];

  return (
    <div className="relative flex-1 flex items-center justify-center overflow-hidden py-6 group">
      {/* Left arrow */}
      <button
        type="button"
        aria-label="Previous fighter"
        onClick={prev}
        className="absolute left-8 top-1/2 -translate-y-1/2 w-14 h-14 rounded-[14px] bg-[var(--color-parchment)] border border-[var(--color-sand)] grid place-items-center shadow-[var(--shadow-paper)] opacity-0 group-hover:opacity-100 transition-opacity z-10 hover:bg-[var(--color-persimmon)] hover:text-[var(--color-parchment)] hover:[&>svg]:stroke-[var(--color-parchment)]"
      >
        <ChevronLeft className="w-[22px] h-[22px] stroke-[var(--color-ink)] transition-all" strokeWidth={2} />
      </button>

      <div className="flex items-center justify-center gap-9 w-full">
        {fighters.length > 1 && (
          <FighterCard
            fighter={prevFighter}
            variant="peek"
            bookmark={renderBookmark(prevFighter)}
          />
        )}
        <FighterCard
          fighter={focus}
          variant="focus"
          bookmark={renderBookmark(focus)}
        />
        {fighters.length > 1 && (
          <FighterCard
            fighter={nextFighter}
            variant="peek"
            bookmark={renderBookmark(nextFighter)}
          />
        )}
      </div>

      {/* Right arrow */}
      <button
        type="button"
        aria-label="Next fighter"
        onClick={next}
        className="absolute right-8 top-1/2 -translate-y-1/2 w-14 h-14 rounded-[14px] bg-[var(--color-parchment)] border border-[var(--color-sand)] grid place-items-center shadow-[var(--shadow-paper)] opacity-0 group-hover:opacity-100 transition-opacity z-10 hover:bg-[var(--color-persimmon)] hover:text-[var(--color-parchment)] hover:[&>svg]:stroke-[var(--color-parchment)]"
      >
        <ChevronRight className="w-[22px] h-[22px] stroke-[var(--color-ink)] transition-all" strokeWidth={2} />
      </button>

      {/* Pagination dots */}
      <div className="absolute bottom-6 left-1/2 -translate-x-1/2 flex gap-2">
        {fighters.map((f, i) => (
          <button
            key={f.id}
            type="button"
            aria-label={`Go to ${f.name}`}
            onClick={() => useCarouselStore.getState().setIndex(i)}
            className={
              i === index
                ? "h-1.5 w-[22px] rounded-[4px] bg-[var(--color-persimmon)]"
                : "h-1.5 w-1.5 rounded-full bg-[var(--color-ink)] opacity-20"
            }
          />
        ))}
      </div>
    </div>
  );
}
