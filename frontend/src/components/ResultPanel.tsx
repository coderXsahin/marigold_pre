import type { PredictionResult } from "../types";
import "./ResultPanel.css";

interface Props {
  result: PredictionResult | null;
  loading?: boolean;
}

export default function ResultPanel({ result, loading }: Props) {
  if (loading) {
    return (
      <div className="result-panel loading">
        <div className="pulse-ring" />
        <p>Running model inference…</p>
      </div>
    );
  }

  if (!result) {
    return (
      <div className="result-panel empty">
        <div className="empty-icon" aria-hidden>?</div>
        <p>Your diagnosis will appear here after you run analysis.</p>
      </div>
    );
  }

  const healthy = result.is_healthy;
  const confidencePct =
    result.confidence != null ? `${Math.round(result.confidence * 100)}%` : null;

  return (
    <div className={`result-panel ${healthy ? "healthy" : "diseased"}`}>
      <div className="result-header">
        <span className={`result-badge ${healthy ? "healthy" : "diseased"}`}>
          {healthy ? "Healthy" : "Disease detected"}
        </span>
        {confidencePct && (
          <span className="confidence-ring" title="Confidence">
            {confidencePct}
          </span>
        )}
      </div>
      <h2 className="disease-title">{result.disease_name}</h2>
      {result.note && <p className="details note">{result.note}</p>}
      {!healthy && result.details && <p className="details">{result.details}</p>}
    </div>
  );
}
