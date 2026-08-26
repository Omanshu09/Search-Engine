import React from "react";
import SourceList from "./SourceList.jsx";

/**
 * Renders a synthesized research answer plus its supporting sources.
 * `data` shape matches the backend ResearchResponse model.
 * TODO: parse inline citation markers (e.g. [1], [2]) in data.answer and
 * link them to the matching entry in data.sources.
 */
export default function ResearchAnswer({ data }) {
  if (!data) return null;
  return (
    <div className="research-answer">
      <p>{data.answer}</p>
      <h4>Sources</h4>
      <SourceList sources={data.sources} />
    </div>
  );
}
