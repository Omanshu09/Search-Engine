import React from "react";

export default function Loading({ label = "Loading..." }) {
  // TODO: replace with a proper spinner/skeleton once visual design is settled.
  return <div className="loading">{label}</div>;
}
