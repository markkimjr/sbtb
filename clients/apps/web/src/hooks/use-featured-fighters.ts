"use client";

import { ApiError, apiClient } from "@/lib/api-client";
import type { FeaturedFighter } from "@/types/fighter";
import { useQuery } from "@tanstack/react-query";

const TEN_MINUTES = 10 * 60 * 1000;

export const FEATURED_FIGHTERS_QUERY_KEY = ["fighters", "featured"] as const;

export function useFeaturedFighters() {
  return useQuery<FeaturedFighter[]>({
    queryKey: FEATURED_FIGHTERS_QUERY_KEY,
    queryFn: async () => {
      const { data, error, response } = await apiClient.GET("/api/fighter/featured");
      if (error || !data) {
        throw new ApiError(response.status, error?.detail?.toString() ?? response.statusText);
      }
      return data;
    },
    staleTime: TEN_MINUTES,
  });
}
