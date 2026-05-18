import { useCallback, useEffect, useState } from "react";
import { fetchHistory, predictImage } from "../api";
import ImageUpload from "../components/ImageUpload";
import ResultPanel from "../components/ResultPanel";
import StatsChart from "../components/StatsChart";
import type { HealthStatus, HistoryEntry, PredictionResult } from "../types";
import "./Dashboard.css";

interface Props {
  health: HealthStatus | null;
}

export default function Dashboard({ health }: Props) {
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<PredictionResult | null>(null);
  const [history, setHistory] = useState<HistoryEntry[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadHistory = useCallback(async () => {
    try {
      const data = await fetchHistory();
      setHistory(data);
    } catch {
      /* ignore on dashboard */
    }
  }, []);

  useEffect(() => {
    loadHistory();
  }, [loadHistory]);

  const handleAnalyze = async () => {
    if (!file) {
      setError("Please select an image first");
      return;
    }
    setError(null);
    setLoading(true);
    setResult(null);
    try {
      const data = await predictImage(file);
      setResult(data);
      await loadHistory();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Prediction failed");
    } finally {
      setLoading(false);
    }
  };

  const modelReady = health?.ml?.model_loaded ?? false;
  const healthyCount = history.filter((h) => h.is_healthy).length;
  const diseasedCount = history.filter((h) => !h.is_healthy).length;

  return (
    <div className="dashboard">
      <header className="page-header">
        <div>
          <p className="eyebrow">Disease detection</p>
          <h2>Scan your marigold</h2>
          <p className="subtitle">
            Upload a leaf or plant photo to classify health and spot common diseases.
          </p>
        </div>
      </header>

      {!modelReady && (
        <div className="banner warning" role="alert">
          <strong>Model not loaded.</strong> Train with{" "}
          <code>notebooks/train_model.ipynb</code> and place <code>ml/model.h5</code> before
          analyzing.
        </div>
      )}

      <div className="kpi-row">
        <article className="kpi">
          <span className="kpi-label">Total scans</span>
          <span className="kpi-value">{history.length}</span>
        </article>
        <article className="kpi healthy">
          <span className="kpi-label">Healthy</span>
          <span className="kpi-value">{healthyCount}</span>
        </article>
        <article className="kpi diseased">
          <span className="kpi-label">Diseased</span>
          <span className="kpi-value">{diseasedCount}</span>
        </article>
      </div>

      <div className="workspace">
        <section className="panel upload-panel">
          <div className="panel-head">
            <span className="step">1</span>
            <h3>Upload image</h3>
          </div>
          <ImageUpload onFileSelect={setFile} disabled={loading} />
          <button
            type="button"
            className="btn-analyze"
            onClick={handleAnalyze}
            disabled={!file || loading || !modelReady}
          >
            {loading ? (
              <>
                <span className="btn-spinner" />
                Analyzing…
              </>
            ) : (
              "Run analysis"
            )}
          </button>
          {error && <p className="form-error">{error}</p>}
        </section>

        <section className="panel result-panel-wrap">
          <div className="panel-head">
            <span className="step">2</span>
            <h3>Diagnosis</h3>
          </div>
          <ResultPanel result={result} loading={loading} />
        </section>
      </div>

      <section className="panel analytics-panel">
        <div className="panel-head">
          <h3>Analytics</h3>
          <p className="panel-desc">Distribution of past scans</p>
        </div>
        <StatsChart history={history} />
      </section>
    </div>
  );
}
