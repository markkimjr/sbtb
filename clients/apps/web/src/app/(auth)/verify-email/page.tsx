import { VerifyEmailScreen } from "@/features/auth/components/verify-email-screen";
import { Suspense } from "react";

export default function VerifyEmailPage() {
  return (
    <Suspense>
      <VerifyEmailScreen />
    </Suspense>
  );
}
