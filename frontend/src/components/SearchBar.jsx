import React, { useState } from "react";

/**
 * Controlled search input. Calls onSubmit(query) on Enter/submit.
 */
export default function SearchBar({ onSubmit, placeholder = "Search the web..." }) {
  const [value, setValue] = useState("");

  function handleSubmit(e) {
    e.preventDefault();
    if (value.trim()) onSubmit(value.trim());
  }

  return (
    <form onSubmit={handleSubmit} className="search-bar">
      <input
        type="text"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder={placeholder}
      />
      <button type="submit">Search</button>
    </form>
  );
}
