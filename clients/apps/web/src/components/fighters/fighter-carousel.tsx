"use client";

import { useCarouselStore } from "@/store/carousel";
import type { FeaturedFighter } from "@/types/fighter";
import { type PanInfo, motion } from "framer-motion";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { type ReactNode, useEffect } from "react";
import { FighterCard } from "./fighter-card";

// Card geometry — must stay in sync with FighterCard's `w-[320px]`.
const CARD_WIDTH = 320;
const CARD_GAP = 36;
// Horizontal distance between two adjacent card centers.
const SLOT = CARD_WIDTH + CARD_GAP;

// "Swipe power" blends how far the cursor dragged with how fast it was flung.
// Velocity (px/s) is scaled down to be comparable with the pixel offset.
const VELOCITY_WEIGHT = 0.2;
// Minimum power before a swipe registers at all.
const SWIPE_TRIGGER_POWER = 80;
// Power required to advance one additional fighter — higher = harder to skip multiple.
const SWIPE_POWER_PER_STEP = 320;
// Safety cap so a hard fling can't fly across the whole list in one go.
const MAX_SWIPE_STEPS = 8;

const SLIDE_TRANSITION = { type: "spring", stiffness: 280, damping: 32 } as const;

type FighterCarouselProps = {
  fighters: FeaturedFighter[];
  renderBookmark: (fighter: FeaturedFighter) => ReactNode;
};

export function FighterCarousel({ fighters, renderBookmark }: FighterCarouselProps) {
  const { index, setTotal, setIndex } = useCarouselStore();
  const count = fighters.length;
  const swipeable = count > 1;

  // Clamp helper — the filmstrip stops at the ends rather than wrapping.
  const goTo = (target: number) => setIndex(Math.max(0, Math.min(target, count - 1)));

  useEffect(() => {
    setTotal(count);
  }, [count, setTotal]);

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (e.key === "ArrowLeft") setIndex(useCarouselStore.getState().index - 1);
      if (e.key === "ArrowRight") setIndex(useCarouselStore.getState().index + 1);
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [setIndex]);

  if (count === 0) {
    return (
      <div className="flex-1 grid place-items-center">
        <p className="text-sm opacity-60">No fighters match your search.</p>
      </div>
    );
  }

  function handleDragEnd(_: unknown, info: PanInfo) {
    const { offset, velocity } = info;
    // Combine distance and fling speed into a single signed "power" value.
    // Negative = dragged left (advance forward); positive = dragged right (go back).
    const power = offset.x + velocity.x * VELOCITY_WEIGHT;
    if (Math.abs(power) < SWIPE_TRIGGER_POWER) return;
    const steps = Math.min(
      MAX_SWIPE_STEPS,
      Math.max(1, Math.round(Math.abs(power) / SWIPE_POWER_PER_STEP)),
    );
    goTo(index + (power < 0 ? steps : -steps));
  }

  return (
    <div className="relative flex-1 flex items-center overflow-hidden py-6 group">
      {/* Left arrow */}
      <button
        type="button"
        aria-label="Previous fighter"
        onClick={() => goTo(index - 1)}
        disabled={index === 0}
        className="absolute left-8 top-1/2 -translate-y-1/2 w-14 h-14 rounded-[14px] bg-[var(--color-parchment)] border border-[var(--color-sand)] grid place-items-center shadow-[var(--shadow-paper)] opacity-0 group-hover:opacity-100 disabled:!opacity-0 transition-opacity z-10 cursor-pointer hover:bg-[var(--color-persimmon)] hover:text-[var(--color-parchment)] hover:[&>svg]:stroke-[var(--color-parchment)]"
      >
        <ChevronLeft
          className="w-[22px] h-[22px] stroke-[var(--color-ink)] transition-all"
          strokeWidth={2}
        />
      </button>

      {/* Filmstrip track — all fighters laid out horizontally, slid to center the active one. */}
      <motion.div
        className={`flex items-center select-none will-change-transform ${
          swipeable ? "cursor-grab active:cursor-grabbing" : ""
        }`}
        style={{
          gap: CARD_GAP,
          // Pad so the first/last card can sit dead-center of the viewport.
          paddingLeft: `calc(50% - ${CARD_WIDTH / 2}px)`,
          paddingRight: `calc(50% - ${CARD_WIDTH / 2}px)`,
        }}
        drag={swipeable ? "x" : false}
        dragConstraints={{ left: -(count - 1) * SLOT, right: 0 }}
        dragElastic={0.12}
        onDragEnd={handleDragEnd}
        animate={{ x: -index * SLOT }}
        transition={SLIDE_TRANSITION}
      >
        {fighters.map((fighter, i) => (
          <FighterCard
            key={fighter.id}
            fighter={fighter}
            variant={i === index ? "focus" : "peek"}
            bookmark={renderBookmark(fighter)}
          />
        ))}
      </motion.div>

      {/* Right arrow */}
      <button
        type="button"
        aria-label="Next fighter"
        onClick={() => goTo(index + 1)}
        disabled={index === count - 1}
        className="absolute right-8 top-1/2 -translate-y-1/2 w-14 h-14 rounded-[14px] bg-[var(--color-parchment)] border border-[var(--color-sand)] grid place-items-center shadow-[var(--shadow-paper)] opacity-0 group-hover:opacity-100 disabled:!opacity-0 transition-opacity z-10 cursor-pointer hover:bg-[var(--color-persimmon)] hover:text-[var(--color-parchment)] hover:[&>svg]:stroke-[var(--color-parchment)]"
      >
        <ChevronRight
          className="w-[22px] h-[22px] stroke-[var(--color-ink)] transition-all"
          strokeWidth={2}
        />
      </button>
    </div>
  );
}
