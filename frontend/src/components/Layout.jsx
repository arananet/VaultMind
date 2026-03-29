import { useState } from "react";
import { Outlet, NavLink } from "react-router-dom";

const NAV_ITEMS = [
  { path: "/", label: "Query Vault", icon: ">" },
  { path: "/guides", label: "Guides", icon: "#" },
  { path: "/map", label: "Offline Map", icon: "@" },
  { path: "/diagnostics", label: "Diagnostics", icon: "!" },
];

export default function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="app-layout">
      <aside className={`sidebar ${sidebarOpen ? "open" : ""}`}>
        <div className="sidebar-logo">
          VAULTMIND
          <span className="sidebar-subtitle">Protocol Zero</span>
        </div>
        <nav className="sidebar-nav" role="navigation" aria-label="Main navigation">
          {NAV_ITEMS.map(({ path, label, icon }) => (
            <NavLink
              key={path}
              to={path}
              end={path === "/"}
              className={({ isActive }) =>
                `nav-link ${isActive ? "active" : ""}`
              }
              onClick={() => setSidebarOpen(false)}
            >
              <span aria-hidden="true">{icon}</span>
              {label}
            </NavLink>
          ))}
        </nav>
        <div style={{ marginTop: "auto", fontSize: "0.6875rem", color: "var(--color-text-muted)" }}>
          Air-gapped. Zero telemetry.
          <br />
          All processing is local.
        </div>
      </aside>

      <div className="mobile-header">
        <button
          className="mobile-menu-btn"
          onClick={() => setSidebarOpen(!sidebarOpen)}
          aria-label="Toggle navigation menu"
        >
          &#9776;
        </button>
        <span style={{ fontFamily: "var(--font-mono)", fontWeight: 700, color: "var(--color-accent)" }}>
          VAULTMIND
        </span>
      </div>

      <main className="main-content" role="main">
        <Outlet />
      </main>
    </div>
  );
}
