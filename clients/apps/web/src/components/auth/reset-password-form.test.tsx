import { cleanup, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { ResetPasswordForm } from "@/components/auth/reset-password-form";
import { mockRouter } from "@/test-utils/router";
import { mockSupabase } from "@/test-utils/supabase";

const supabase = mockSupabase();
const router = mockRouter();
const toastError = vi.fn();
const toastSuccess = vi.fn();

vi.mock("@/lib/supabase/browser", () => ({ createClient: () => supabase }));
vi.mock("next/navigation", () => ({ useRouter: () => router }));
vi.mock("sonner", () => ({
  toast: {
    error: (m: string) => toastError(m),
    success: (m: string) => toastSuccess(m),
  },
}));

describe("ResetPasswordForm", () => {
  beforeEach(() => {
    supabase.auth.getUser.mockResolvedValue({
      data: { user: { id: "u1" } },
      error: null,
    });
  });

  afterEach(() => {
    cleanup();
    vi.clearAllMocks();
  });

  it("redirects to /forgot-password when no recovery session", async () => {
    supabase.auth.getUser.mockResolvedValueOnce({
      data: { user: null },
      error: null,
    });

    render(<ResetPasswordForm />);

    await waitFor(() =>
      expect(router.push).toHaveBeenCalledWith("/forgot-password"),
    );
    expect(toastError).toHaveBeenCalled();
  });

  it("submits valid password and routes to /fighters", async () => {
    supabase.auth.updateUser.mockResolvedValueOnce({
      data: { user: { id: "u1" } },
      error: null,
    });
    const user = userEvent.setup();

    render(<ResetPasswordForm />);
    await waitFor(() => expect(screen.getByLabelText(/^new password/i)).toBeEnabled());

    await user.type(screen.getByLabelText(/^new password/i), "newpassword123");
    await user.type(screen.getByLabelText(/confirm/i), "newpassword123");
    await user.click(screen.getByRole("button", { name: /set password/i }));

    expect(supabase.auth.updateUser).toHaveBeenCalledWith({
      password: "newpassword123",
    });
    expect(router.push).toHaveBeenCalledWith("/fighters");
  });

  it("shows validation error on mismatched confirm", async () => {
    const user = userEvent.setup();
    render(<ResetPasswordForm />);
    await waitFor(() => expect(screen.getByLabelText(/^new password/i)).toBeEnabled());

    await user.type(screen.getByLabelText(/^new password/i), "newpassword123");
    await user.type(screen.getByLabelText(/confirm/i), "different");
    await user.click(screen.getByRole("button", { name: /set password/i }));

    expect(supabase.auth.updateUser).not.toHaveBeenCalled();
    expect(screen.getByText(/passwords don't match/i)).toBeInTheDocument();
  });

  it("surfaces server error as toast", async () => {
    supabase.auth.updateUser.mockResolvedValueOnce({
      data: { user: null },
      error: { message: "Password too weak" },
    });
    const user = userEvent.setup();

    render(<ResetPasswordForm />);
    await waitFor(() => expect(screen.getByLabelText(/^new password/i)).toBeEnabled());

    await user.type(screen.getByLabelText(/^new password/i), "newpassword123");
    await user.type(screen.getByLabelText(/confirm/i), "newpassword123");
    await user.click(screen.getByRole("button", { name: /set password/i }));

    expect(toastError).toHaveBeenCalledWith("Password too weak");
  });
});
