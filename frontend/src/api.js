/**
 * Thin fetch wrapper around the ATLAS backend API.
 *
 * In local dev, "/api" is proxied to the backend by Vite (see vite.config.js).
 * In production, frontend and backend are deployed separately, so
 * VITE_API_BASE_URL must be set at build time to the backend's public URL
 * (e.g. "https://atlas-backend.onrender.com/api"). Set it in your hosting
 * provider's environment variables, or in a .env file (see .env.example).
 */
const BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";

async function request(path, options = {}) {
  const response = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) {
    throw new Error(`ATLAS API error ${response.status}: ${await response.text()}`);
  }
  return response.json();
}

export function search(query, options = {}) {
  return request("/search/", {
    method: "POST",
    body: JSON.stringify({ query, top_k: 10, use_semantic_search: true, ...options }),
  });
}

export function research(question, options = {}) {
  return request("/research/", {
    method: "POST",
    body: JSON.stringify({ question, max_sources: 8, depth: "standard", ...options }),
  });
}

export function submitFeedback(payload) {
  return request("/feedback/", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
