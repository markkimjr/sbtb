"use client";

import { ApiError, apiClient } from "@/lib/api-client";
import { createClient } from "@/lib/supabase/browser";
import type { Schemas } from "@sbtb/client";
import type { User as SupabaseUser } from "@supabase/supabase-js";
import { useQuery } from "@tanstack/react-query";

export const CURRENT_USER_QUERY_KEY = ["auth", "current-user"] as const;

type CurrentUserData = {
  supabaseUser: SupabaseUser | null;
  profile: Schemas["UserMeRead"] | null;
};

async function fetchCurrentUser(): Promise<CurrentUserData> {
  const supabase = createClient();
  const {
    data: { user: supabaseUser },
  } = await supabase.auth.getUser();

  if (!supabaseUser) {
    return { supabaseUser: null, profile: null };
  }

  const result = (await apiClient.GET("/api/user/me")) as {
    data?: Schemas["UserMeRead"];
    error?: { detail?: unknown };
    response: Response;
  };
  const { data, error, response } = result;
  if (error || !data) {
    const apiError = new ApiError(
      response.status,
      error?.detail?.toString() ?? response.statusText,
    );
    // Attach the Supabase user so consumers can still render UI that depends
    // on the authenticated identity (e.g. avatar initial) while surfacing the
    // backend profile fetch failure separately.
    (apiError as ApiError & { supabaseUser?: SupabaseUser }).supabaseUser = supabaseUser;
    throw apiError;
  }

  return { supabaseUser, profile: data };
}

export function useCurrentUser() {
  const query = useQuery({
    queryKey: CURRENT_USER_QUERY_KEY,
    queryFn: fetchCurrentUser,
    staleTime: Number.POSITIVE_INFINITY,
  });

  const errorWithUser = query.error as (Error & { supabaseUser?: SupabaseUser }) | null;

  return {
    supabaseUser: query.data?.supabaseUser ?? errorWithUser?.supabaseUser ?? null,
    profile: query.data?.profile ?? null,
    isLoading: query.isLoading,
    error: query.error,
  };
}
