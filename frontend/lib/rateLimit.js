import { loadEnvConfig } from "@next/env";
import path from "node:path";

loadEnvConfig(path.resolve(process.cwd(), ".."));

import { createClient } from "redis";

const REDIS_URL = process.env.REDIS_URL;

if (!REDIS_URL) {
  throw new Error("REDIS_URL is not configured.");
}

// Reuse the same Redis connection during Next.js development
// instead of creating a new connection for every request.
const globalForRedis = globalThis;

if (!globalForRedis.matchPilotRedis) {
  globalForRedis.matchPilotRedis = createClient({
    url: process.env.REDIS_URL || "redis://localhost:6739",
    RESP: 2,
  });

  globalForRedis.matchPilotRedis.on("error", (error) => {
    console.error("Redis connection error:", error);
  });
}

const redis = globalForRedis.matchPilotRedis;

let connectionPromise = null;

async function connectRedis() {
  if (redis.isReady) return;

  if (!connectionPromise) {
    connectionPromise = redis.connect().finally(() => {
      connectionPromise = null;
    });
  }

  await connectionPromise;
}

const RATE_LIMIT_SCRIPT = `
  local current = redis.call("INCR", KEYS[1])

  if current == 1 then
    redis.call("PEXPIRE", KEYS[1], ARGV[1])
  end

  local ttl = redis.call("PTTL", KEYS[1])

  return { current, ttl }
`;

export async function checkRateLimit(
  request,
  {
    limit = 30,
    windowMs = 60 * 1000,
    prefix = "api",
  } = {}
) {
  try {
    await connectRedis();

    const forwardedFor = request.headers.get("x-forwarded-for");
    const realIp = request.headers.get("x-real-ip");

    const ip =
      forwardedFor?.split(",")[0]?.trim() ||
      realIp ||
      "unknown";

    const key = `matchpilot:rate-limit:${prefix}:${ip}`;

    const result = await redis.eval(RATE_LIMIT_SCRIPT, {
      keys: [key],
      arguments: [String(windowMs)],
    });

    const [current, ttl] = result;

    const count = Number(current);
    const retryAfter = Math.max(
      1,
      Math.ceil(Number(ttl) / 1000)
    );

    return {
      allowed: count <= limit,
      limit,
      remaining: Math.max(0, limit - count),
      retryAfter,
    };
  } catch (error) {
    console.error("Rate limiter error:", error);

    // Fail closed: do not allow requests through if Redis
    // is unavailable and the rate limit cannot be checked.
    return {
      allowed: false,
      unavailable: true,
      limit,
      remaining: 0,
      retryAfter: 60,
    };
  }
}
