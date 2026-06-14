import { create } from "zustand";

type ModalState = {
  firstBookmark: { open: boolean; fighterId: string | null };
  openFirstBookmark: (fighterId: string) => void;
  closeFirstBookmark: () => void;

  bookmarks: Set<string>;
  hasSeenIntro: boolean;
  addBookmark: (id: string) => void;
  removeBookmark: (id: string) => void;
  markIntroSeen: () => void;
};

export const useModalStore = create<ModalState>((set) => ({
  firstBookmark: { open: false, fighterId: null },
  openFirstBookmark: (fighterId) =>
    set({ firstBookmark: { open: true, fighterId } }),
  closeFirstBookmark: () =>
    set({ firstBookmark: { open: false, fighterId: null } }),

  bookmarks: new Set<string>(),
  hasSeenIntro: false,
  addBookmark: (id) =>
    set((s) => ({ bookmarks: new Set(s.bookmarks).add(id) })),
  removeBookmark: (id) =>
    set((s) => {
      const next = new Set(s.bookmarks);
      next.delete(id);
      return { bookmarks: next };
    }),
  markIntroSeen: () => set({ hasSeenIntro: true }),
}));
