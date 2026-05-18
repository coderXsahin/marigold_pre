import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { fetchHistory } from "../api";
import type { HistoryEntry } from "../types";
import "./History.css";

export default function History() {
  const [entries, setEntries] = useState<HistoryEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchHistory()
      .then(setEntries)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="history-page">
        <p className="history-status">Loading scan history…</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="history-page">
        <p className="history-status error">{error}</p>
      </div>
    );
  }

  return (
    <div className="history-page">
      <header className="page-header">
        <div>
          <p className="eyebrow">Past scans</p>
          <h2>Scan history</h2>
          <p className="subtitle">{entries.length} recorded analyses</p>
        </div>
        <Link to="/" className="btn-new-scan">
          New scan
        </Link>
      </header>

      {entries.length === 0 ? (
        <div className="history-empty">
          <p>No predictions yet.</p>
          <Link to="/" className="btn-new-scan">
            Run your first scan
          </Link>
        </div>
      ) : (
        <div className="history-grid">
          {entries.map((entry) => (
            <article key={entry.id} className={`history-card ${entry.is_healthy ? "healthy" : "diseased"}`}>
              <div className="card-image-wrap">
                <img src={`/${entry.thumbnail}`} alt={entry.prediction} className="card-image" />
                <span className={`card-badge ${entry.is_healthy ? "healthy" : "diseased"}`}>
                  {entry.is_healthy ? "Healthy" : "Diseased"}
                </span>
              </div>
              <div className="card-body">
                <h3>{entry.prediction}</h3>
                {entry.confidence && <p className="conf">{entry.confidence} confidence</p>}
                {entry.details && <p className="details">{entry.details}</p>}
                <time dateTime={entry.timestamp}>
                  {new Date(entry.timestamp).toLocaleString()}
                </time>
              </div>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}
