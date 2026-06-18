import { renderHook, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { useCurrentUser } from "@/hooks/use-current-user";
import { createQueryWrapper } from "@/test-utils/query-wrapper";
import { mockSupabase } from "@/test-utils/supabase";

const supabase = mockSupabase();
const apiGet = vi.fn();

vi.mock("@/lib/supabase/browser", () => ({
  createClient: () => supabase,
}));

vi.mock("@/lib/api-client", () => ({
  apiClient: { GET: (...args: unknown[]) => apiGet(...args) },
  ApiError: class ApiError extends Error {
    constructor(
      public status: number,
      public detail: string,
    ) {
      super(detail);
    }
  },
}));

describe("useCurrentUser", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.resetAllMocks();
  });

  it("returns null shape when no Supabase user", async () => {
    supabase.auth.getUser.mockResolvedValueOnce({
      data: { user: null },
      error: null,
    });

    const { result } = renderHook(() => useCurrentUser(), {
      wrapper: createQueryWrapper(),
    });

    await waitFor(() => expect(result.current.isLoading).toBe(false));
    expect(result.current.supabaseUser).toBeNull();
    expect(result.current.profile).toBeNull();
    expect(apiGet).not.toHaveBeenCalled();
  });

  it("merges Supabase user and backend profile when both succeed", async () => {
    supabase.auth.getUser.mockResolvedValue({
      data: { user: { id: "u1", email: "a@b.co" } },
      error: null,
    });
    apiGet.mockResolvedValue({
      data: { id: "u1", email: "a@b.co", isActive: true, isSuperuser: false },
      error: undefined,
      response: { ok: true, status: 200 },
    });

    const { result } = renderHook(() => useCurrentUser(), {
      wrapper: createQueryWrapper(),
    });

    await waitFor(() => expect(result.current.profile).not.toBeNull());
    expect(result.current.supabaseUser?.id).toBe("u1");
    expect(result.current.profile?.id).toBe("u1");
    expect(result.current.profile?.isActive).toBe(true);
  });

  it("surfaces ApiError when /user/me fails", async () => {
    supabase.auth.getUser.mockResolvedValue({
      data: { user: { id: "u1", email: "a@b.co" } },
      error: null,
    });
    apiGet.mockResolvedValue({
      data: undefined,
      error: { detail: "Invalid token" },
      response: { ok: false, status: 401, statusText: "Unauthorized" },
    });

    const { result } = renderHook(() => useCurrentUser(), {
      wrapper: createQueryWrapper(),
    });

    await waitFor(() => expect(result.current.error).not.toBeNull());
    expect(result.current.supabaseUser?.id).toBe("u1");
    expect(result.current.profile).toBeNull();
  });
});
