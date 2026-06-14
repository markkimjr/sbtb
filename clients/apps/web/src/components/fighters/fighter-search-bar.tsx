"use client";

import { Search } from "lucide-react";
import { useEffect, useState } from "react";
import { useDebouncedCallback } from "use-debounce";

type FighterSearchBarProps = {
  onChange: (query: string) => void;
};

export function FighterSearchBar({ onChange }: FighterSearchBarProps) {
  const [value, setValue] = useState("");
  const debouncedEmit = useDebouncedCallback(onChange, 250);

  useEffect(() => {
    debouncedEmit(value);
  }, [value, debouncedEmit]);

  return (
    <div className="flex items-center gap-2 bg-[color-mix(in_srgb,white_25%,transparent)] border border-[var(--color-sand)] rounded-full px-4 py-2.5 w-[360px]">
      <Search className="w-4 h-4 opacity-50" strokeWidth={1.75} />
      <input
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder="Search by name — Inoue, Crawford, Canelo…"
        className="bg-transparent border-0 outline-none flex-1 text-sm min-w-0 text-[var(--color-ink)] placeholder:opacity-50"
      />
    </div>
  );
}
