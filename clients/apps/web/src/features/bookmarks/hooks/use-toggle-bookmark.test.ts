import { useBookmarkStore } from "@/features/bookmarks/store/bookmarks";
import { act, renderHook } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

const mockPush = vi.fn();
vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: mockPush, refresh: vi.fn() }),
  usePathname: () => "/fighters",
}));

vi.mock("@/hooks/use-current-user", () => ({
  useCurrentUser: vi.fn(),
}));

import { useCurrentUser } from "@/hooks/use-current-user";
import { useToggleBookmark } from "./use-toggle-bookmark";

const mockedUseCurrentUser = vi.mocked(useCurrentUser);

describe("useToggleBookmark", () => {
  beforeEach(() => {
    mockPush.mockReset();
    useBookmarkStore.setState({
      bookmarks: new Set(),
      hasSeenIntro: false,
      firstBookmark: { open: false, fighterId: null },
    });
  });

  it("redirects to signup when unauthenticated", () => {
    mockedUseCurrentUser.mockReturnValue({
      supabaseUser: null,
    } as ReturnType<typeof useCurrentUser>);
    const { result } = renderHook(() => useToggleBookmark());

    act(() => {
      result.current.toggle("inoue");
    });

    expect(mockPush).toHaveBeenCalledWith("/signup?next=%2Ffighters&fighter=inoue");
  });

  it("opens first-bookmark modal on first save when authed + no prior bookmarks", () => {
    mockedUseCurrentUser.mockReturnValue({
      supabaseUser: { id: "u1" },
    } as ReturnType<typeof useCurrentUser>);
    const { result } = renderHook(() => useToggleBookmark());

    act(() => {
      result.current.toggle("inoue");
    });

    const state = useBookmarkStore.getState();
    expect(state.firstBookmark.open).toBe(true);
    expect(state.firstBookmark.fighterId).toBe("inoue");
    expect(state.bookmarks.has("inoue")).toBe(false);
  });

  it("silently toggles after intro is seen", () => {
    mockedUseCurrentUser.mockReturnValue({
      supabaseUser: { id: "u1" },
    } as ReturnType<typeof useCurrentUser>);
    useBookmarkStore.setState({ hasSeenIntro: true });
    const { result } = renderHook(() => useToggleBookmark());

    act(() => {
      result.current.toggle("inoue");
    });

    expect(useBookmarkStore.getState().bookmarks.has("inoue")).toBe(true);
    expect(useBookmarkStore.getState().firstBookmark.open).toBe(false);
  });

  it("toggles off an already-bookmarked fighter without modal", () => {
    mockedUseCurrentUser.mockReturnValue({
      supabaseUser: { id: "u1" },
    } as ReturnType<typeof useCurrentUser>);
    useBookmarkStore.setState({
      hasSeenIntro: true,
      bookmarks: new Set(["inoue"]),
    });
    const { result } = renderHook(() => useToggleBookmark());

    act(() => {
      result.current.toggle("inoue");
    });

    expect(useBookmarkStore.getState().bookmarks.has("inoue")).toBe(false);
  });
});
