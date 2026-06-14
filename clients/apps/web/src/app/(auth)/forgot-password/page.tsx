import Link from "next/link";
import { ForgotPasswordForm } from "@/components/auth/forgot-password-form";

export default function ForgotPasswordPage() {
  return (
    <div className="space-y-6">
      <header className="space-y-2 text-center">
        <h1 className="font-display italic text-3xl">Reset your password.</h1>
        <p className="text-sm opacity-70">
          We&apos;ll email you a link to set a new one.
        </p>
      </header>
      <ForgotPasswordForm />
      <p className="text-center text-sm opacity-70">
        Remembered it?{" "}
        <Link href="/login" className="font-medium hover:underline">
          Back to log in
        </Link>
      </p>
    </div>
  );
}
