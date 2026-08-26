import React, { useState } from "react";
import SearchBar from "../components/SearchBar.jsx";
import ResearchAnswer from "../components/ResearchAnswer.jsx";
import Loading from "../components/Loading.jsx";
import { research } from "../api.js";

/**
 * Research page: ask a question, get a synthesized, cited answer
 * (see ATLAS's Search vs. Research distinction).
 */
export default function Research() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function handleAsk(question) {
    setLoading(true);
    setError(null);
    try {
      const result = await research(question);
      setData(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <SearchBar onSubmit={handleAsk} placeholder="Ask a question..." />
      {loading && <Loading label="Researching..." />}
      {error && <p className="error">{error}</p>}
      {!loading && <ResearchAnswer data={data} />}
    </div>
  );
}
