import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import { SetPasswordBanner } from "@/components/profile/set-password-banner";

const useCurrentUserMock = vi.fn();

vi.mock("@/hooks/use-current-user", () => ({
  useCurrentUser: () => useCurrentUserMock(),
}));

vi.mock("@/components/profile/set-password-form", () => ({
  SetPasswordForm: ({ onPasswordSet }: { onPasswordSet: () => void }) => (
    <button type="button" onClick={onPasswordSet}>
      [stub set-password-form]
    </button>
  ),
}));

describe("SetPasswordBanner", () => {
  afterEach(() => {
    cleanup();
    vi.clearAllMocks();
  });

  it("renders when user has only OAuth identities", () => {
    useCurrentUserMock.mockReturnValue({
      supabaseUser: {
        id: "u1",
        identities: [{ provider: "google" }],
      },
    });

    render(<SetPasswordBanner />);
    expect(screen.getByRole("button", { name: /set a password/i })).toBeInTheDocument();
  });

  it("hides when user has an email identity", () => {
    useCurrentUserMock.mockReturnValue({
      supabaseUser: {
        id: "u1",
        identities: [{ provider: "email" }, { provider: "google" }],
      },
    });

    const { container } = render(<SetPasswordBanner />);
    expect(container).toBeEmptyDOMElement();
  });

  it("hides when no supabase user", () => {
    useCurrentUserMock.mockReturnValue({ supabaseUser: null });
    const { container } = render(<SetPasswordBanner />);
    expect(container).toBeEmptyDOMElement();
  });

  it("unmounts after onPasswordSet fires", async () => {
    useCurrentUserMock.mockReturnValue({
      supabaseUser: {
        id: "u1",
        identities: [{ provider: "google" }],
      },
    });
    const user = userEvent.setup();

    const { container } = render(<SetPasswordBanner />);
    // Expand the form
    await user.click(screen.getByRole("button", { name: /set a password/i }));
    // Click the stub form's "set password" trigger
    await user.click(screen.getByRole("button", { name: /stub set-password-form/i }));

    expect(container).toBeEmptyDOMElement();
  });
});
