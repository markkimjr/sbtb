import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import { MagicLinkButton } from "@/features/auth/components/magic-link-button";
import { mockSupabase } from "@/test-utils/supabase";

const supabase = mockSupabase();
const toastSuccess = vi.fn();
const toastError = vi.fn();

vi.mock("@/lib/supabase/browser", () => ({ createClient: () => supabase }));
vi.mock("sonner", () => ({
  toast: {
    success: (m: string) => toastSuccess(m),
    error: (m: string) => toastError(m),
  },
}));

describe("MagicLinkButton", () => {
  afterEach(() => {
    cleanup();
    vi.clearAllMocks();
  });

  it("requires email before calling Supabase", async () => {
    const user = userEvent.setup();
    render(<MagicLinkButton />);
    await user.click(screen.getByRole("button", { name: /send.*link/i }));
    expect(supabase.auth.signInWithOtp).not.toHaveBeenCalled();
    expect(screen.getByText(/enter a valid email/i)).toBeInTheDocument();
  });

  it("calls signInWithOtp with the right redirect and starts cooldown", async () => {
    const user = userEvent.setup();

    render(<MagicLinkButton />);
    await user.type(screen.getByLabelText(/email/i), "x@y.co");
    await user.click(screen.getByRole("button", { name: /send.*link/i }));

    expect(supabase.auth.signInWithOtp).toHaveBeenCalledWith({
      email: "x@y.co",
      options: {
        emailRedirectTo: expect.stringContaining("/auth/callback?next=/fighters"),
      },
    });
    expect(toastSuccess).toHaveBeenCalled();

    // Button disabled during cooldown
    expect(screen.getByRole("button", { name: /resend in/i })).toBeDisabled();
  });

  it("surfaces rate-limit error as toast", async () => {
    const user = userEvent.setup();
    supabase.auth.signInWithOtp.mockResolvedValueOnce({
      data: {},
      error: { code: "over_email_send_rate_limit", message: "Too many requests" },
    });

    render(<MagicLinkButton />);
    await user.type(screen.getByLabelText(/email/i), "x@y.co");
    await user.click(screen.getByRole("button", { name: /send.*link/i }));

    expect(toastError).toHaveBeenCalled();
  });
});
