import { create } from "zustand";

type CarouselState = {
  index: number;
  total: number;
  next: () => void;
  prev: () => void;
  advance: (delta: number) => void;
  setIndex: (i: number) => void;
  setTotal: (total: number) => void;
};

export const useCarouselStore = create<CarouselState>((set, get) => ({
  index: 0,
  total: 0,
  next: () => {
    const { index, total } = get();
    if (total === 0) return;
    set({ index: (index + 1) % total });
  },
  prev: () => {
    const { index, total } = get();
    if (total === 0) return;
    set({ index: (index - 1 + total) % total });
  },
  advance: (delta) => {
    const { index, total } = get();
    if (total === 0) return;
    set({ index: (((index + delta) % total) + total) % total });
  },
  setIndex: (i) => {
    const { total } = get();
    if (total === 0) return;
    set({ index: Math.max(0, Math.min(i, total - 1)) });
  },
  setTotal: (total) => {
    const { index } = get();
    set({ total, index: index >= total ? 0 : index });
  },
}));
