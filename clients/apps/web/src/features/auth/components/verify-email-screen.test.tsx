import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { VerifyEmailScreen } from "@/features/auth/components/verify-email-screen";
import { mockSearchParams } from "@/test-utils/router";
import { mockSupabase } from "@/test-utils/supabase";

const supabase = mockSupabase();
const toastSuccess = vi.fn();
const toastError = vi.fn();
let searchParams = mockSearchParams({ email: "u@example.com" });

vi.mock("@/lib/supabase/browser", () => ({ createClient: () => supabase }));
vi.mock("next/navigation", () => ({
  useSearchParams: () => searchParams,
}));
vi.mock("sonner", () => ({
  toast: {
    success: (m: string) => toastSuccess(m),
    error: (m: string) => toastError(m),
  },
}));

describe("VerifyEmailScreen", () => {
  beforeEach(() => {
    searchParams = mockSearchParams({ email: "u@example.com" });
  });

  afterEach(() => {
    cleanup();
    vi.clearAllMocks();
  });

  it("displays the email from the query param", () => {
    render(<VerifyEmailScreen />);
    expect(screen.getByText(/u@example.com/i)).toBeInTheDocument();
  });

  it("shows error state when email param missing", () => {
    searchParams = mockSearchParams();
    render(<VerifyEmailScreen />);
    expect(screen.getByText(/sign up first/i)).toBeInTheDocument();
  });

  it("Resend success: shows toast and disables button with countdown", async () => {
    const user = userEvent.setup();
    render(<VerifyEmailScreen />);

    await user.click(screen.getByRole("button", { name: /resend/i }));

    expect(supabase.auth.resend).toHaveBeenCalledWith({
      type: "signup",
      email: "u@example.com",
    });
    expect(toastSuccess).toHaveBeenCalled();
    expect(screen.getByRole("button", { name: /resend in/i })).toBeDisabled();
  });

  it("Rate limit surfaces specific toast", async () => {
    const user = userEvent.setup();
    supabase.auth.resend.mockResolvedValueOnce({
      data: {},
      error: { code: "over_email_send_rate_limit", message: "Too many requests" },
    });

    render(<VerifyEmailScreen />);
    await user.click(screen.getByRole("button", { name: /resend/i }));

    expect(toastError).toHaveBeenCalled();
  });
});
