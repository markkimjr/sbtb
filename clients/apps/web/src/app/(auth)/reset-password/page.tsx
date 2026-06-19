import { ResetPasswordForm } from "@/features/auth/components/reset-password-form";
import { Suspense } from "react";

export default function ResetPasswordPage() {
  return (
    <div className="space-y-6">
      <header className="space-y-2 text-center">
        <h1 className="font-display italic text-3xl">Set a new password.</h1>
        <p className="text-sm opacity-70">Pick something memorable.</p>
      </header>
      <Suspense>
        <ResetPasswordForm />
      </Suspense>
    </div>
  );
}
