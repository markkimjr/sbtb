"use client";

import { useQuery } from "@tanstack/react-query";
import { createClient } from "@/lib/supabase/browser";

export const USER_QUERY_KEY = ["auth", "user"] as const;

export function useUser() {
  return useQuery({
    queryKey: USER_QUERY_KEY,
    queryFn: async () => {
      const supabase = createClient();
      const {
        data: { user },
      } = await supabase.auth.getUser();
      return user;
    },
    staleTime: Number.POSITIVE_INFINITY,
  });
}
