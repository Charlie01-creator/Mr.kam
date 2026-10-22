/**
 * Fixed-window in-memory limiter. LIMITATION: state is per server instance,
 * so on Vercel serverless it only slows casual abuse. Swap for a shared store
 * (e.g. Upstash Redis) before relying on it for login protection.
 */
const hits = new Map<string, { count: number; resetAt: number }>();

export function rateLimit(key: string, limit: number, windowMs: number, now = Date.now()) {
  const h = hits.get(key);
  if (!h || h.resetAt <= now) {
    hits.set(key, { count: 1, resetAt: now + windowMs });
    return { ok: true, remaining: limit - 1 };
  }
  h.count++;
  return { ok: h.count <= limit, remaining: Math.max(0, limit - h.count) };
}
