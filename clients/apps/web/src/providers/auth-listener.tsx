"use client";

import { useQueryClient } from "@tanstack/react-query";
import { useEffect } from "react";
import { USER_QUERY_KEY } from "@/hooks/use-user";
import { createClient } from "@/lib/supabase/browser";

export function AuthListener() {
  const queryClient = useQueryClient();

  useEffect(() => {
    const supabase = createClient();
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange(() => {
      queryClient.invalidateQueries({ queryKey: USER_QUERY_KEY });
    });
    return () => subscription.unsubscribe();
  }, [queryClient]);

  return null;
}
