"use client";

import { useSearchParams } from "next/navigation";
import { useEffect } from "react";
import { toast } from "sonner";

export function LoginErrorToast() {
  const params = useSearchParams();
  const error = params.get("error");

  useEffect(() => {
    if (error) toast.error(decodeURIComponent(error));
  }, [error]);

  return null;
}
