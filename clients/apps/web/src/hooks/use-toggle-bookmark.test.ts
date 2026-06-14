import { act, renderHook } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { useModalStore } from "@/store/modal";

const mockPush = vi.fn();
vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: mockPush, refresh: vi.fn() }),
  usePathname: () => "/fighters",
}));

vi.mock("./use-user", () => ({
  useUser: vi.fn(),
}));

import { useUser } from "./use-user";
import { useToggleBookmark } from "./use-toggle-bookmark";

const mockedUseUser = vi.mocked(useUser);

describe("useToggleBookmark", () => {
  beforeEach(() => {
    mockPush.mockReset();
    useModalStore.setState({
      bookmarks: new Set(),
      hasSeenIntro: false,
      firstBookmark: { open: false, fighterId: null },
    });
  });

  it("redirects to signup when unauthenticated", () => {
    mockedUseUser.mockReturnValue({ data: null } as ReturnType<typeof useUser>);
    const { result } = renderHook(() => useToggleBookmark());

    act(() => {
      result.current.toggle("inoue");
    });

    expect(mockPush).toHaveBeenCalledWith(
      "/signup?next=%2Ffighters&fighter=inoue",
    );
  });

  it("opens first-bookmark modal on first save when authed + no prior bookmarks", () => {
    mockedUseUser.mockReturnValue({ data: { id: "u1" } } as ReturnType<typeof useUser>);
    const { result } = renderHook(() => useToggleBookmark());

    act(() => {
      result.current.toggle("inoue");
    });

    const state = useModalStore.getState();
    expect(state.firstBookmark.open).toBe(true);
    expect(state.firstBookmark.fighterId).toBe("inoue");
    expect(state.bookmarks.has("inoue")).toBe(false);
  });

  it("silently toggles after intro is seen", () => {
    mockedUseUser.mockReturnValue({ data: { id: "u1" } } as ReturnType<typeof useUser>);
    useModalStore.setState({ hasSeenIntro: true });
    const { result } = renderHook(() => useToggleBookmark());

    act(() => {
      result.current.toggle("inoue");
    });

    expect(useModalStore.getState().bookmarks.has("inoue")).toBe(true);
    expect(useModalStore.getState().firstBookmark.open).toBe(false);
  });

  it("toggles off an already-bookmarked fighter without modal", () => {
    mockedUseUser.mockReturnValue({ data: { id: "u1" } } as ReturnType<typeof useUser>);
    useModalStore.setState({
      hasSeenIntro: true,
      bookmarks: new Set(["inoue"]),
    });
    const { result } = renderHook(() => useToggleBookmark());

    act(() => {
      result.current.toggle("inoue");
    });

    expect(useModalStore.getState().bookmarks.has("inoue")).toBe(false);
  });
});
