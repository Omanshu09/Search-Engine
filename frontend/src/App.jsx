import React from "react";
import { BrowserRouter, Routes, Route, NavLink } from "react-router-dom";
import Home from "./pages/Home.jsx";
import Research from "./pages/Research.jsx";

/**
 * Top-level app shell: nav between Search (Home) and Research pages.
 * TODO: add auth/session context here once accounts exist.
 */
export default function App() {
  return (
    <BrowserRouter>
      <header className="atlas-header">
        <span className="atlas-logo">ATLAS</span>
        <nav>
          <NavLink to="/" end>
            Search
          </NavLink>
          <NavLink to="/research">Research</NavLink>
        </nav>
      </header>
      <main>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/research" element={<Research />} />
        </Routes>
      </main>
    </BrowserRouter>
  );
}
