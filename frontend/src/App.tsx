import { useEffect, useState } from "react";
import { NavLink, Route, Routes } from "react-router-dom";
import { fetchHealth } from "./api";
import Dashboard from "./pages/Dashboard";
import History from "./pages/History";
import type { HealthStatus } from "./types";
import "./App.css";

export default function App() {
  const [health, setHealth] = useState<HealthStatus | null>(null);

  useEffect(() => {
    fetchHealth().then(setHealth).catch(() => null);
  }, []);

  const modelReady = health?.ml?.model_loaded ?? false;

  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="sidebar-brand">
          <span className="logo-mark" aria-hidden>
            M
          </span>
          <div>
            <h1>Marigold</h1>
            <p>Plant health AI</p>
          </div>
        </div>

        <nav className="sidebar-nav">
          <NavLink to="/" end className={({ isActive }) => (isActive ? "active" : "")}>
            <span className="nav-icon" aria-hidden>
              ◎
            </span>
            Scan
          </NavLink>
          <NavLink to="/history" className={({ isActive }) => (isActive ? "active" : "")}>
            <span className="nav-icon" aria-hidden>
              ≡
            </span>
            History
          </NavLink>
        </nav>

        <div className="sidebar-footer">
          <div className={`model-status ${modelReady ? "ready" : "offline"}`}>
            <span className="status-dot" />
            {modelReady ? "Model ready" : "Model offline"}
          </div>
        </div>
      </aside>

      <main className="content">
        <Routes>
          <Route path="/" element={<Dashboard health={health} />} />
          <Route path="/history" element={<History />} />
        </Routes>
      </main>
    </div>
  );
}
