import React from "react";
import ResultCard from "./ResultCard.jsx";

export default function SearchResults({ results = [] }) {
  if (results.length === 0) {
    return <p className="empty-state">No results yet.</p>;
  }
  return (
    <div className="search-results">
      {results.map((r) => (
        <ResultCard key={r.id} result={r} />
      ))}
    </div>
  );
}
