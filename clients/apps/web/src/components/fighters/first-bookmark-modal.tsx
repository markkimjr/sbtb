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
import { MOCK_FIGHTERS } from "@/lib/mock-fighters";
import { useModalStore } from "@/store/modal";

export function FirstBookmarkModal() {
  const { firstBookmark, closeFirstBookmark, addBookmark, markIntroSeen } =
    useModalStore();

  const fighter = MOCK_FIGHTERS.find((f) => f.id === firstBookmark.fighterId);

  function onConfirm() {
    if (firstBookmark.fighterId) {
      addBookmark(firstBookmark.fighterId);
      markIntroSeen();
    }
    closeFirstBookmark();
  }

  return (
    <Dialog
      open={firstBookmark.open}
      onOpenChange={(o) => !o && closeFirstBookmark()}
    >
      <DialogContent>
        <DialogHeader>
          <DialogTitle className="font-display italic text-2xl">
            One quick thing.
          </DialogTitle>
          <DialogDescription className="pt-2">
            We&apos;ll let you know when{" "}
            <span className="font-medium text-[var(--color-ink)]">
              {fighter?.name ?? "your fighter"}
            </span>{" "}
            is scheduled to fight next, and one day before each fight. You can
            change these times in your profile.
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
