import cors from "cors";
import express from "express";
import fs from "fs/promises";
import path from "path";
import { fileURLToPath } from "url";
import multer from "multer";
import fetch from "node-fetch";
import FormData from "form-data";
import { v4 as uuidv4 } from "uuid";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.join(__dirname, "..");
const UPLOADS_DIR = path.join(ROOT, "uploads");
const HISTORY_PATH = path.join(ROOT, "history.json");
const ML_URL = process.env.ML_URL || "http://127.0.0.1:8000";
const PORT = process.env.PORT || 3001;

const ALLOWED_MIME = new Set(["image/jpeg", "image/png", "image/jpg"]);

const storage = multer.diskStorage({
  destination: async (_req, _file, cb) => {
    await fs.mkdir(UPLOADS_DIR, { recursive: true });
    cb(null, UPLOADS_DIR);
  },
  filename: (_req, file, cb) => {
    const ext = path.extname(file.originalname).toLowerCase() || ".jpg";
    cb(null, `${uuidv4()}${ext}`);
  },
});

const upload = multer({
  storage,
  limits: { fileSize: 10 * 1024 * 1024 },
  fileFilter: (_req, file, cb) => {
    if (!ALLOWED_MIME.has(file.mimetype)) {
      return cb(new Error("Only JPG and PNG images are allowed"));
    }
    cb(null, true);
  },
});

const app = express();
app.use(cors());
app.use(express.json());
app.use("/uploads", express.static(UPLOADS_DIR));

async function readHistory() {
  try {
    const raw = await fs.readFile(HISTORY_PATH, "utf-8");
    return JSON.parse(raw);
  } catch {
    return [];
  }
}

async function writeHistory(entries) {
  await fs.writeFile(HISTORY_PATH, JSON.stringify(entries, null, 2));
}

function formatConfidence(confidence) {
  if (confidence == null) return null;
  const pct = typeof confidence === "number" ? confidence * 100 : parseFloat(confidence) * 100;
  return `${Math.round(pct)}%`;
}

app.get("/api/health", async (_req, res) => {
  try {
    const mlRes = await fetch(`${ML_URL}/health`);
    const ml = await mlRes.json();
    res.json({ backend: "ok", ml });
  } catch {
    res.json({ backend: "ok", ml: { status: "unreachable", model_loaded: false } });
  }
});

app.get("/api/history", async (_req, res) => {
  const history = await readHistory();
  res.json(history);
});

app.post("/api/predict", upload.single("image"), async (req, res) => {
  if (!req.file) {
    return res.status(400).json({ error: "No image uploaded" });
  }

  try {
    const form = new FormData();
    const fileBuffer = await fs.readFile(req.file.path);
    form.append("file", fileBuffer, {
      filename: req.file.filename,
      contentType: req.file.mimetype,
    });

    const mlRes = await fetch(`${ML_URL}/predict`, {
      method: "POST",
      body: form,
      headers: form.getHeaders(),
    });

    if (!mlRes.ok) {
      const err = await mlRes.json().catch(() => ({ detail: mlRes.statusText }));
      return res.status(mlRes.status).json({ error: err.detail || "ML prediction failed" });
    }

    const prediction = await mlRes.json();
    const entry = {
      id: uuidv4(),
      thumbnail: `uploads/${req.file.filename}`,
      prediction: prediction.disease_name,
      confidence:
        prediction.confidence != null ? formatConfidence(prediction.confidence) : null,
      is_healthy: prediction.is_healthy,
      details: prediction.details || null,
      timestamp: new Date().toISOString(),
    };

    const history = await readHistory();
    history.unshift(entry);
    await writeHistory(history);

    res.json({ ...prediction, historyEntry: entry });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: err.message || "Prediction failed" });
  }
});

app.use((err, _req, res, _next) => {
  if (err instanceof multer.MulterError || err.message?.includes("JPG")) {
    return res.status(400).json({ error: err.message });
  }
  res.status(500).json({ error: err.message || "Server error" });
});

const server = app.listen(PORT, () => {
  console.log(`Backend running on http://localhost:${PORT}`);
});

server.on("error", (err) => {
  if (err.code === "EADDRINUSE") {
    console.error(
      `Port ${PORT} is already in use. Close the other backend terminal or run:\n` +
        `  netstat -ano | findstr :${PORT}\n` +
        `  taskkill /PID <pid> /F`
    );
  } else {
    console.error(err);
  }
  process.exit(1);
});
