import { GoogleOAuthButton } from "@/features/auth/components/google-oauth-button";
import { LoginErrorToast } from "@/features/auth/components/login-error-toast";
import { LoginForm } from "@/features/auth/components/login-form";
import { MagicLinkButton } from "@/features/auth/components/magic-link-button";
import Link from "next/link";
import { Suspense } from "react";

export default function LoginPage() {
  return (
    <div className="space-y-6">
      <Suspense>
        <LoginErrorToast />
      </Suspense>
      <header className="space-y-2 text-center">
        <h1 className="font-display italic text-3xl">Welcome back.</h1>
        <p className="text-sm opacity-70">Log in to manage your fighters and notifications.</p>
      </header>

      <div className="space-y-4">
        <Suspense>
          <GoogleOAuthButton label="Continue with Google" />
        </Suspense>
        <div className="flex items-center gap-3 text-xs opacity-60">
          <div className="flex-1 h-px bg-[var(--color-sand)]" />
          <span>or</span>
          <div className="flex-1 h-px bg-[var(--color-sand)]" />
        </div>
      </div>

      <Suspense>
        <LoginForm />
      </Suspense>

      <div className="pt-2 border-t border-[var(--color-sand)]">
        <p className="text-xs opacity-60 text-center mb-2">Trouble logging in?</p>
        <Suspense>
          <MagicLinkButton />
        </Suspense>
      </div>

      <div className="space-y-2 text-center text-sm">
        <Link href="/forgot-password" className="opacity-70 hover:opacity-100 underline block">
          Forgot your password?
        </Link>
        <p className="opacity-70">
          New here?{" "}
          <Link href="/signup" className="font-medium hover:underline">
            Sign up
          </Link>
        </p>
      </div>
    </div>
  );
}
