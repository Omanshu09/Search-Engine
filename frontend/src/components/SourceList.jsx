import React from "react";

/**
 * Renders the list of sources used in a research answer, numbered to
 * match inline citation markers rendered by ResearchAnswer.jsx.
 */
export default function SourceList({ sources = [] }) {
  if (sources.length === 0) return null;
  return (
    <ol className="source-list">
      {sources.map((s) => (
        <li key={s.id}>
          <a href={s.url} target="_blank" rel="noreferrer">
            {s.title}
          </a>{" "}
          <span className="source-domain">({s.domain})</span>
        </li>
      ))}
    </ol>
  );
}
