export interface PredictionResult {
  is_healthy: boolean;
  disease_name: string;
  confidence?: number;
  details?: string;
  note?: string;
  historyEntry?: HistoryEntry;
}

export interface HistoryEntry {
  id: string;
  thumbnail: string;
  prediction: string;
  confidence: string | null;
  is_healthy: boolean;
  details: string | null;
  timestamp: string;
}

export interface HealthStatus {
  backend: string;
  ml: {
    status?: string;
    model_loaded: boolean;
    classes?: number;
  };
}
