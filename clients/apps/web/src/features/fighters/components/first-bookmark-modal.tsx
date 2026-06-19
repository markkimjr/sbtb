"use client";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { useBookmarkStore } from "@/features/bookmarks/store/bookmarks";
import { useFeaturedFighters } from "@/features/fighters/hooks/use-featured-fighters";

export function FirstBookmarkModal() {
  const { firstBookmark, closeFirstBookmark, addBookmark, markIntroSeen } = useBookmarkStore();
  const { data: fighters = [] } = useFeaturedFighters();

  const fighter = fighters.find((f) => f.id === firstBookmark.fighterId);

  function onConfirm() {
    if (firstBookmark.fighterId) {
      addBookmark(firstBookmark.fighterId);
      markIntroSeen();
    }
    closeFirstBookmark();
  }

  return (
    <Dialog open={firstBookmark.open} onOpenChange={(o) => !o && closeFirstBookmark()}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle className="font-display italic text-2xl">One quick thing.</DialogTitle>
          <DialogDescription className="pt-2">
            We&apos;ll let you know when{" "}
            <span className="font-medium text-[var(--color-ink)]">
              {fighter?.name ?? "your fighter"}
            </span>{" "}
            is scheduled to fight next, and one day before each fight. You can change these times in
            your profile.
          </DialogDescription>
        </DialogHeader>
        <DialogFooter>
          <Button onClick={onConfirm} className="w-full">
            Got it — save fighter
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
