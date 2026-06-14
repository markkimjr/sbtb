"use client";

import { useState } from "react";
import { toast } from "sonner";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";

type Timing = "when_scheduled" | "one_week" | "three_days" | "one_day" | "one_hour";

const TIMINGS: { id: Timing; label: string }[] = [
  { id: "when_scheduled", label: "When a fight is first scheduled" },
  { id: "one_week", label: "1 week before" },
  { id: "three_days", label: "3 days before" },
  { id: "one_day", label: "1 day before" },
  { id: "one_hour", label: "1 hour before" },
];

const DEFAULT_SELECTED: Set<Timing> = new Set(["when_scheduled", "one_day"]);

export function NotificationPreferences() {
  const [selected, setSelected] = useState<Set<Timing>>(DEFAULT_SELECTED);

  function onToggle(id: Timing, checked: boolean) {
    const next = new Set(selected);
    if (checked) next.add(id);
    else next.delete(id);
    setSelected(next);
    toast("Saved");
  }

  return (
    <section className="space-y-4">
      <div className="space-y-1">
        <h2 className="font-display italic text-2xl">Notification preferences</h2>
        <p className="text-sm opacity-70">When should we let you know?</p>
      </div>

      <div className="space-y-3">
        {TIMINGS.map((t) => (
          <div key={t.id} className="flex items-center gap-3">
            <Checkbox
              id={t.id}
              checked={selected.has(t.id)}
              onCheckedChange={(c) => onToggle(t.id, c === true)}
            />
            <Label htmlFor={t.id} className="text-sm font-normal cursor-pointer">
              {t.label}
            </Label>
          </div>
        ))}
      </div>
    </section>
  );
}
