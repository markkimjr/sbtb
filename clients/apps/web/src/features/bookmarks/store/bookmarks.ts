import { create } from "zustand";

type BookmarkState = {
  // Bookmark domain state — the set of saved fighter ids.
  bookmarks: Set<string>;
  hasSeenIntro: boolean;
  addBookmark: (id: string) => void;
  removeBookmark: (id: string) => void;
  markIntroSeen: () => void;

  // First-bookmark onboarding modal ("one quick thing") shown on the first ever save.
  firstBookmark: { open: boolean; fighterId: string | null };
  openFirstBookmark: (fighterId: string) => void;
  closeFirstBookmark: () => void;
};

export const useBookmarkStore = create<BookmarkState>((set) => ({
  bookmarks: new Set<string>(),
  hasSeenIntro: false,
  addBookmark: (id) => set((s) => ({ bookmarks: new Set(s.bookmarks).add(id) })),
  removeBookmark: (id) =>
    set((s) => {
      const next = new Set(s.bookmarks);
      next.delete(id);
      return { bookmarks: next };
    }),
  markIntroSeen: () => set({ hasSeenIntro: true }),

  firstBookmark: { open: false, fighterId: null },
  openFirstBookmark: (fighterId) => set({ firstBookmark: { open: true, fighterId } }),
  closeFirstBookmark: () => set({ firstBookmark: { open: false, fighterId: null } }),
}));
