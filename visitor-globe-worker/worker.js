const STATS_KEY = "visitor-globe:v1:stats";
const DEFAULT_ALLOWED_ORIGIN = "https://wanghongjian98.github.io";

function allowedOrigin(env) {
  return env.ALLOWED_ORIGIN || DEFAULT_ALLOWED_ORIGIN;
}

function corsHeaders(origin, env) {
  const allowOrigin = origin === allowedOrigin(env) ? origin : allowedOrigin(env);
  return {
    "Access-Control-Allow-Origin": allowOrigin,
    "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Max-Age": "86400",
  };
}

function json(data, init = {}) {
  return new Response(JSON.stringify(data), {
    ...init,
    headers: {
      "Content-Type": "application/json; charset=utf-8",
      "Cache-Control": "no-store",
      ...(init.headers || {}),
    },
  });
}

async function sha256(text) {
  const bytes = new TextEncoder().encode(text);
  const digest = await crypto.subtle.digest("SHA-256", bytes);
  return [...new Uint8Array(digest)].map((byte) => byte.toString(16).padStart(2, "0")).join("");
}

async function readStats(env) {
  return (
    (await env.VISITOR_GLOBE.get(STATS_KEY, "json")) || {
      totalVisits: 0,
      updatedAt: "",
      points: [],
    }
  );
}

async function writeStats(env, stats) {
  await env.VISITOR_GLOBE.put(STATS_KEY, JSON.stringify(stats));
}

function locationFromRequest(request) {
  const cf = request.cf || {};
  const country = cf.country || "Unknown";
  const region = cf.region || "";
  const city = cf.city || "";
  const lat = Number(cf.latitude);
  const lon = Number(cf.longitude);
  const label = [city, region, country].filter(Boolean).join(", ") || country;

  return {
    key: [country, region, city, Number.isFinite(lat) ? lat.toFixed(3) : "", Number.isFinite(lon) ? lon.toFixed(3) : ""].join("|"),
    label,
    country,
    region,
    city,
    lat: Number.isFinite(lat) ? lat : null,
    lon: Number.isFinite(lon) ? lon : null,
  };
}

function clientIp(request) {
  return request.headers.get("CF-Connecting-IP") || "";
}

async function handleCollect(request, env) {
  const now = new Date();
  const today = now.toISOString().slice(0, 10);
  const ip = clientIp(request);
  const salt = env.HASH_SALT || "development-salt-change-before-deploy";
  const visitorHash = ip ? await sha256(`${salt}:${today}:${ip}`) : "";
  const seenKey = visitorHash ? `visitor-globe:v1:seen:${today}:${visitorHash}` : "";
  const alreadySeen = seenKey ? await env.VISITOR_GLOBE.get(seenKey) : null;

  if (seenKey && !alreadySeen) {
    await env.VISITOR_GLOBE.put(seenKey, "1", { expirationTtl: 60 * 60 * 48 });
  }

  const location = locationFromRequest(request);
  const stats = await readStats(env);
  const existing = stats.points.find((point) => point.key === location.key);
  const point =
    existing ||
    {
      ...location,
      visits: 0,
      uniqueDailyVisitors: 0,
    };

  point.firstSeenAt ||= now.toISOString();
  point.lastSeenAt = now.toISOString();
  point.visits += 1;
  if (!alreadySeen) point.uniqueDailyVisitors += 1;

  if (!existing) stats.points.push(point);
  stats.totalVisits += 1;
  stats.updatedAt = now.toISOString();
  stats.points = stats.points.sort((a, b) => b.visits - a.visits).slice(0, 250);

  await writeStats(env, stats);
  return new Response(null, { status: 204 });
}

async function handleStats(env, origin) {
  const stats = await readStats(env);
  return json(
    {
      totalVisits: stats.totalVisits,
      updatedAt: stats.updatedAt,
      points: stats.points.map((point) => ({
        label: point.label,
        country: point.country,
        region: point.region,
        city: point.city,
        lat: point.lat,
        lon: point.lon,
        visits: point.visits,
        uniqueDailyVisitors: point.uniqueDailyVisitors,
        lastSeenAt: point.lastSeenAt,
      })),
    },
    { headers: corsHeaders(origin, env) },
  );
}

export default {
  async fetch(request, env) {
    const origin = request.headers.get("Origin") || "";
    const url = new URL(request.url);

    if (request.method === "OPTIONS") {
      return new Response(null, { headers: corsHeaders(origin, env) });
    }

    if (url.pathname === "/collect" && request.method === "POST") {
      const response = await handleCollect(request, env);
      return new Response(response.body, { status: response.status, headers: corsHeaders(origin, env) });
    }

    if (url.pathname === "/stats" && request.method === "GET") {
      return handleStats(env, origin);
    }

    return json({ error: "Not found" }, { status: 404, headers: corsHeaders(origin, env) });
  },
};
