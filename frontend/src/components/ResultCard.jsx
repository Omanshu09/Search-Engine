import React from "react";

/**
 * Single search result: title (linked), domain, snippet.
 * `result` shape matches backend SearchResultItem model.
 */
export default function ResultCard({ result }) {
  return (
    <div className="result-card">
      <a href={result.url} target="_blank" rel="noreferrer">
        <h3>{result.title}</h3>
      </a>
      <div className="result-domain">{result.source_domain}</div>
      <p>{result.snippet}</p>
    </div>
  );
}
