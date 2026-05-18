# Deployment guide

This app has **three services**:

| Service  | Stack              | Role                                      |
|----------|--------------------|-------------------------------------------|
| `ml`     | FastAPI + TensorFlow | Image classification (port 8000 internal) |
| `backend`| Node.js + Express  | API, uploads, history (port 3001 internal) |
| `frontend` | React + nginx    | UI + reverse proxy (port **8080** public)  |

---

## Before you deploy

1. **Train the model** (if you have not already):

   ```powershell
   python notebooks\split_dataset.py
   python -m pip install tensorflow scipy
   python notebooks\train_model.py
   ```

2. Confirm these files exist:

   - `ml/model.weights.h5` (or `ml/model.h5`)
   - `ml/class_indices.json`

3. Install **Docker Desktop** (Windows/Mac) or Docker Engine (Linux).

---

## Option A — Docker Compose (recommended)

From the project root:

```powershell
cd e:\disease-prediction
docker compose up --build
```

First build can take **10–20 minutes** (TensorFlow image is large).

Open the app: **http://localhost:8080**

Stop:

```powershell
docker compose down
```

Run in background:

```powershell
docker compose up --build -d
docker compose logs -f
```

### Check health

```powershell
curl http://localhost:8080/api/health
```

`ml.model_loaded` should be `true` when weights are mounted correctly.

### Common issues

| Problem | Fix |
|---------|-----|
| `model.weights.h5` mount error | Train first; file must exist (not a folder). On Windows, use an absolute path if needed. |
| Sidebar shows “Model offline” | Check `docker compose logs ml` for load errors. |
| Port 8080 in use | Change `8080:80` in `docker-compose.yml` to e.g. `3000:80`. |
| ML container exits | Needs ~2 GB RAM; increase Docker Desktop memory. |

---

## Option B — VPS (Ubuntu) with Docker

1. Copy the project to the server (git clone or `scp`).
2. Train locally or copy `ml/model.weights.h5` + `class_indices.json` to the server.
3. Install Docker: https://docs.docker.com/engine/install/ubuntu/
4. Run:

   ```bash
   cd disease-prediction
   docker compose up --build -d
   ```

5. Open firewall port **8080** (or put nginx/Caddy in front on 80/443).

### HTTPS with Caddy (example)

```
yourdomain.com {
    reverse_proxy localhost:8080
}
```

---

## Option C — Run without Docker (manual)

Three terminals from project root:

```powershell
# 1 — ML
cd ml
python -m pip install -r requirements.txt
python -m uvicorn server:app --host 0.0.0.0 --port 8000

# 2 — Backend
cd backend
npm install
$env:ML_URL="http://127.0.0.1:8000"
npm start

# 3 — Frontend (dev)
cd frontend
npm install
npm run dev
```

Dev UI: **http://localhost:5173** (Vite proxies `/api` to backend).

### Production-style frontend (no Docker)

```powershell
cd frontend
npm run build
npm run preview
```

Serve `frontend/dist` with nginx and proxy `/api` and `/uploads` to `http://127.0.0.1:3001` (see `deploy/nginx.conf`).

---

## Environment variables

| Variable   | Service  | Default                 | Description        |
|------------|----------|-------------------------|--------------------|
| `ML_URL`   | backend  | `http://127.0.0.1:8000` | ML service URL     |
| `PORT`     | backend  | `3001`                  | Backend port       |
| `DATA_DIR` | backend  | backend root            | `history.json` dir |
| `HOST`     | backend  | `0.0.0.0`               | Bind address       |

Copy `.env.example` if you customize compose with an `env_file`.

---

## Cloud notes

- **TensorFlow** needs substantial RAM (2 GB+). Small free tiers may OOM.
- **Render / Railway**: deploy `ml`, `backend`, and `frontend` as separate services; set `ML_URL` on backend to the ML service URL; frontend needs a reverse proxy or CORS + public API URL changes.
- **Do not commit** `model.weights.h5` (gitignored); upload weights via volume, object storage, or CI secret artifact.

---

## Quick commands

```powershell
npm run docker:up      # build + start
npm run docker:down    # stop
npm run docker:logs    # follow logs
```
