"use client";

import { useToggleBookmark } from "@/features/bookmarks/hooks/use-toggle-bookmark";
import { cn } from "@/lib/utils";
import { motion } from "framer-motion";
import { Bookmark } from "lucide-react";

type BookmarkButtonProps = {
  fighterId: string;
  fighterName: string;
};

export function BookmarkButton({ fighterId, fighterName }: BookmarkButtonProps) {
  const { toggle, isBookmarked } = useToggleBookmark();
  const saved = isBookmarked(fighterId);

  return (
    <motion.button
      type="button"
      aria-label={saved ? `Remove ${fighterName}` : `Save ${fighterName}`}
      onClick={(e) => {
        e.stopPropagation();
        toggle(fighterId, fighterName);
      }}
      whileTap={{ scale: 0.85, rotate: -2 }}
      animate={{ scale: 1 }}
      transition={{ type: "spring", stiffness: 400, damping: 20 }}
      className={cn(
        "absolute top-3.5 right-3.5 w-[42px] h-[42px] rounded-xl grid place-items-center backdrop-blur-sm transition-colors z-20",
        saved
          ? "bg-[var(--color-persimmon)]"
          : "bg-[color-mix(in_srgb,var(--color-parchment)_88%,transparent)]",
      )}
    >
      <Bookmark
        className="w-5 h-5"
        strokeWidth={1.5}
        fill={saved ? "var(--color-parchment)" : "none"}
        stroke={saved ? "var(--color-parchment)" : "var(--color-ink)"}
      />
    </motion.button>
  );
}
