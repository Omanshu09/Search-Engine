/**
 * Thin fetch wrapper around the ATLAS backend API.
 * Base path "/api" is proxied to the backend in dev (see vite.config.js).
 */
const BASE_URL = "/api";

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
