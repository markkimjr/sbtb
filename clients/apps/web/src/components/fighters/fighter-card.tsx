"use client";

import type { ReactNode } from "react";
import { cn } from "@/lib/utils";
import type { Fighter } from "@/types/fighter";

type FighterCardProps = {
  fighter: Fighter;
  variant?: "focus" | "peek" | "compact";
  bookmark?: ReactNode;
};

const VARIANT_CLASSES: Record<string, string> = {
  focus:
    "scale-[1.06] shadow-[var(--shadow-focus-card)] ring-[1.5px] ring-[color-mix(in_srgb,var(--color-persimmon)_25%,transparent)]",
  peek: "blur-[3px] opacity-45 scale-[0.88]",
  compact: "",
};

export function FighterCard({ fighter, variant = "compact", bookmark }: FighterCardProps) {
  return (
    <div
      className={cn(
        "relative bg-[color-mix(in_srgb,white_30%,transparent)] border border-[var(--color-sand)] rounded-[18px] overflow-hidden shadow-[var(--shadow-card-hover)] transition-all duration-300 ease-[cubic-bezier(0.4,0,0.2,1)] w-[320px] aspect-[3/4.4]",
        VARIANT_CLASSES[variant],
      )}
    >
      {/* Portrait area */}
      <div
        className="w-full aspect-square relative"
        style={{ background: fighter.placeholderGradient }}
      >
        {/* Paper grain overlay on portrait */}
        <div
          className="absolute inset-0 pointer-events-none"
          style={{
            backgroundImage:
              "url(\"data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='180' height='180'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2' stitchTiles='stitch'/><feColorMatrix values='0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 0.07 0'/></filter><rect width='100%25' height='100%25' filter='url(%23n)'/></svg>\")",
          }}
        />
        {bookmark}
      </div>

      {/* Card body */}
      <div className="p-5 flex flex-col gap-1.5">
        <div className="font-display italic text-[26px] leading-[1.1] tracking-[-0.015em]">
          {fighter.name}
        </div>
        <div className="text-[11px] uppercase tracking-[0.12em] opacity-65">
          {fighter.weightClass}
        </div>
        <div className="mt-2 text-xs opacity-70 font-mono tracking-wider">
          {fighter.wins}–{fighter.losses}
          {fighter.draws > 0 ? `–${fighter.draws}` : ""} · {fighter.knockouts} KO
        </div>
      </div>
    </div>
  );
}
