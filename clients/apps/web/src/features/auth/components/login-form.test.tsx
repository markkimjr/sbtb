import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { LoginForm } from "@/features/auth/components/login-form";
import { mockRouter, mockSearchParams } from "@/test-utils/router";
import { mockSupabase } from "@/test-utils/supabase";

const supabase = mockSupabase();
const router = mockRouter();
let searchParams = mockSearchParams();

vi.mock("@/lib/supabase/browser", () => ({ createClient: () => supabase }));

vi.mock("next/navigation", () => ({
  useRouter: () => router,
  useSearchParams: () => searchParams,
}));

const toastError = vi.fn();
vi.mock("sonner", () => ({ toast: { error: (m: string) => toastError(m) } }));

describe("LoginForm", () => {
  beforeEach(() => {
    searchParams = mockSearchParams();
  });

  afterEach(() => {
    cleanup();
    vi.clearAllMocks();
  });

  it("routes to /fighters on successful login", async () => {
    supabase.auth.signInWithPassword.mockResolvedValueOnce({
      data: { user: { id: "u1" } },
      error: null,
    });

    render(<LoginForm />);
    await userEvent.type(screen.getByLabelText(/email/i), "a@b.co");
    await userEvent.type(screen.getByLabelText("Password"), "password");
    await userEvent.click(screen.getByRole("button", { name: /log in/i }));

    expect(supabase.auth.signInWithPassword).toHaveBeenCalledWith({
      email: "a@b.co",
      password: "password",
    });
    expect(router.push).toHaveBeenCalledWith("/fighters");
  });

  it("honors ?next= search param", async () => {
    searchParams = mockSearchParams({ next: "/profile" });
    supabase.auth.signInWithPassword.mockResolvedValueOnce({
      data: { user: { id: "u1" } },
      error: null,
    });

    render(<LoginForm />);
    await userEvent.type(screen.getByLabelText(/email/i), "a@b.co");
    await userEvent.type(screen.getByLabelText("Password"), "password");
    await userEvent.click(screen.getByRole("button", { name: /log in/i }));

    expect(router.push).toHaveBeenCalledWith("/profile");
  });

  it("toasts on invalid_credentials, does not navigate", async () => {
    supabase.auth.signInWithPassword.mockResolvedValueOnce({
      data: { user: null },
      error: { code: "invalid_credentials", message: "Invalid login" },
    });

    render(<LoginForm />);
    await userEvent.type(screen.getByLabelText(/email/i), "a@b.co");
    await userEvent.type(screen.getByLabelText("Password"), "wrongpw");
    await userEvent.click(screen.getByRole("button", { name: /log in/i }));

    expect(toastError).toHaveBeenCalled();
    expect(router.push).not.toHaveBeenCalled();
  });

  it("routes to /verify-email on email_not_confirmed", async () => {
    supabase.auth.signInWithPassword.mockResolvedValueOnce({
      data: { user: null },
      error: { code: "email_not_confirmed", message: "Email not confirmed" },
    });

    render(<LoginForm />);
    await userEvent.type(screen.getByLabelText(/email/i), "unverified@x.co");
    await userEvent.type(screen.getByLabelText("Password"), "password");
    await userEvent.click(screen.getByRole("button", { name: /log in/i }));

    expect(router.push).toHaveBeenCalledWith("/verify-email?email=unverified%40x.co");
    expect(toastError).not.toHaveBeenCalled();
  });
});
