import { beforeEach, describe, expect, it } from "vitest";
import { useCarouselStore } from "./carousel";

describe("useCarouselStore", () => {
  beforeEach(() => {
    useCarouselStore.setState({ index: 0, total: 5 });
  });

  it("starts at index 0", () => {
    expect(useCarouselStore.getState().index).toBe(0);
  });

  it("next() advances by 1", () => {
    useCarouselStore.getState().next();
    expect(useCarouselStore.getState().index).toBe(1);
  });

  it("next() wraps around at the end", () => {
    useCarouselStore.setState({ index: 4, total: 5 });
    useCarouselStore.getState().next();
    expect(useCarouselStore.getState().index).toBe(0);
  });

  it("prev() decrements by 1", () => {
    useCarouselStore.setState({ index: 2, total: 5 });
    useCarouselStore.getState().prev();
    expect(useCarouselStore.getState().index).toBe(1);
  });

  it("prev() wraps to the end from 0", () => {
    useCarouselStore.getState().prev();
    expect(useCarouselStore.getState().index).toBe(4);
  });

  it("setIndex() clamps to [0, total-1]", () => {
    useCarouselStore.getState().setIndex(99);
    expect(useCarouselStore.getState().index).toBe(4);
    useCarouselStore.getState().setIndex(-1);
    expect(useCarouselStore.getState().index).toBe(0);
  });

  it("setTotal() resets index to 0 if current index is out of range", () => {
    useCarouselStore.setState({ index: 4, total: 5 });
    useCarouselStore.getState().setTotal(3);
    expect(useCarouselStore.getState().index).toBe(0);
    expect(useCarouselStore.getState().total).toBe(3);
  });
});
