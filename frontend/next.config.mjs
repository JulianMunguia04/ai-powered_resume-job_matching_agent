import path from "node:path";
import nextEnv from "@next/env";

const { loadEnvConfig } = nextEnv;
const { combinedEnv } = loadEnvConfig(path.resolve(process.cwd(), ".."));

/** @type {import('next').NextConfig} */
const nextConfig = {
  // Explicitly expose variables if needed on the client side
  env: {
    NEXT_PUBLIC_API_URL: combinedEnv.NEXT_PUBLIC_API_URL,
    // Or spread all NEXT_PUBLIC_ keys:
    ...Object.fromEntries(
      Object.entries(combinedEnv).filter(([key]) => key.startsWith("NEXT_PUBLIC_"))
    ),
  },
  // ... your existing config
};

export default nextConfig;
