import { GoogleOAuthButton } from "@/features/auth/components/google-oauth-button";
import { SignupForm } from "@/features/auth/components/signup-form";
import Link from "next/link";
import { Suspense } from "react";

export default function SignupPage() {
  return (
    <div className="space-y-6">
      <header className="space-y-2 text-center">
        <h1 className="font-display italic text-3xl">Get on the card.</h1>
        <p className="text-sm opacity-70">Pick your fighters. We&apos;ll ring the bell.</p>
      </header>

      <div className="space-y-4">
        <Suspense>
          <GoogleOAuthButton label="Sign up with Google" />
        </Suspense>
        <div className="flex items-center gap-3 text-xs opacity-60">
          <div className="flex-1 h-px bg-[var(--color-sand)]" />
          <span>or</span>
          <div className="flex-1 h-px bg-[var(--color-sand)]" />
        </div>
      </div>

      <Suspense>
        <SignupForm />
      </Suspense>

      <p className="text-center text-sm opacity-70">
        Already have an account?{" "}
        <Link href="/login" className="font-medium hover:underline">
          Log in
        </Link>
      </p>
    </div>
  );
}
