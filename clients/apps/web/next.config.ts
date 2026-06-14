import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  images: {
    remotePatterns: [
      // Supabase Storage will serve Ghibli portraits — pattern added when wired.
    ],
  },
};

export default nextConfig;
