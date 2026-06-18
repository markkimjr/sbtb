"use client";

import { CURRENT_USER_QUERY_KEY } from "@/hooks/use-current-user";
import { createClient } from "@/lib/supabase/browser";
import { useQueryClient } from "@tanstack/react-query";
import { useEffect } from "react";

export function AuthListener() {
  const queryClient = useQueryClient();

  useEffect(() => {
    const supabase = createClient();
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange(() => {
      queryClient.invalidateQueries({ queryKey: CURRENT_USER_QUERY_KEY });
    });
    return () => subscription.unsubscribe();
  }, [queryClient]);

  return null;
}
