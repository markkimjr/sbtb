import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import { SetPasswordForm } from "@/features/profile/components/set-password-form";
import { mockSupabase } from "@/test-utils/supabase";

const supabase = mockSupabase();
const toastSuccess = vi.fn();
const toastError = vi.fn();
const onSet = vi.fn();

vi.mock("@/lib/supabase/browser", () => ({ createClient: () => supabase }));
vi.mock("sonner", () => ({
  toast: {
    success: (m: string) => toastSuccess(m),
    error: (m: string) => toastError(m),
  },
}));

describe("SetPasswordForm", () => {
  afterEach(() => {
    cleanup();
    vi.clearAllMocks();
  });

  it("submits valid password and fires onPasswordSet", async () => {
    supabase.auth.updateUser.mockResolvedValueOnce({
      data: { user: { id: "u1" } },
      error: null,
    });
    const user = userEvent.setup();

    render(<SetPasswordForm onPasswordSet={onSet} />);
    await user.type(screen.getByLabelText(/^password/i), "supersecret");
    await user.type(screen.getByLabelText(/confirm/i), "supersecret");
    await user.click(screen.getByRole("button", { name: /save password/i }));

    expect(supabase.auth.updateUser).toHaveBeenCalledWith({
      password: "supersecret",
    });
    expect(toastSuccess).toHaveBeenCalled();
    expect(onSet).toHaveBeenCalled();
  });

  it("validation error on mismatched confirm", async () => {
    const user = userEvent.setup();
    render(<SetPasswordForm onPasswordSet={onSet} />);

    await user.type(screen.getByLabelText(/^password/i), "supersecret");
    await user.type(screen.getByLabelText(/confirm/i), "different");
    await user.click(screen.getByRole("button", { name: /save password/i }));

    expect(supabase.auth.updateUser).not.toHaveBeenCalled();
    expect(screen.getByText(/passwords don't match/i)).toBeInTheDocument();
  });

  it("toasts on server error", async () => {
    supabase.auth.updateUser.mockResolvedValueOnce({
      data: { user: null },
      error: { message: "Too weak" },
    });
    const user = userEvent.setup();

    render(<SetPasswordForm onPasswordSet={onSet} />);
    await user.type(screen.getByLabelText(/^password/i), "supersecret");
    await user.type(screen.getByLabelText(/confirm/i), "supersecret");
    await user.click(screen.getByRole("button", { name: /save password/i }));

    expect(toastError).toHaveBeenCalledWith("Too weak");
    expect(onSet).not.toHaveBeenCalled();
  });
});
