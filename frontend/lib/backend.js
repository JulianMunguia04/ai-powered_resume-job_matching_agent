
import { loadEnvConfig } from "@next/env";
import path from "node:path";

// Load the project's root .env file
loadEnvConfig(path.resolve(process.cwd(), ".."));

// Flask backend URL
const BACKEND_URL = process.env.BACKEND_URL;

if (!BACKEND_URL) {
  throw new Error("BACKEND_URL is not configured in the root .env file.");
}

// Remove trailing slashes to avoid malformed URLs
export const backendUrl = BACKEND_URL.replace(/\/+$/, "");

