import React, { useState } from "react";
import SearchBar from "../components/SearchBar.jsx";
import SearchResults from "../components/SearchResults.jsx";
import Loading from "../components/Loading.jsx";
import { search } from "../api.js";

/**
 * Search page: plain "discover sources" experience (see ATLAS's
 * Search vs. Research distinction).
 */
export default function Home() {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function handleSearch(query) {
    setLoading(true);
    setError(null);
    try {
      const data = await search(query);
      setResults(data.results || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <SearchBar onSubmit={handleSearch} />
      {loading && <Loading label="Searching..." />}
      {error && <p className="error">{error}</p>}
      {!loading && <SearchResults results={results} />}
    </div>
  );
}
