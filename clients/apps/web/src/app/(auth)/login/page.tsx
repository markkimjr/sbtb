import Link from "next/link";
import { Suspense } from "react";
import { GoogleOAuthButton } from "@/components/auth/google-oauth-button";
import { LoginForm } from "@/components/auth/login-form";

export default function LoginPage() {
  return (
    <div className="space-y-6">
      <header className="space-y-2 text-center">
        <h1 className="font-display italic text-3xl">Welcome back.</h1>
        <p className="text-sm opacity-70">
          Log in to manage your fighters and notifications.
        </p>
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
