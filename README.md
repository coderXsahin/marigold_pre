# Marigold Disease Detection

Full-stack flower disease detection per [PRD.md](./PRD.md).

## Quick start (local dev)

### 1. Split dataset (train 70% / val 15% / test 15%)

```powershell
python notebooks\split_dataset.py
```

### 2. Train model (GPU recommended; ~3–15 min on Colab, longer on CPU)

```powershell
python -m pip install tensorflow scipy
python notebooks\train_model.py
```

Outputs in `ml/`: `model.weights.h5`, `class_indices.json`, `training_report.json`

See [notebooks/COLAB_TRAIN.md](./notebooks/COLAB_TRAIN.md) for Colab (zip `dataset_split` folder).

### 3. Run the app (3 terminals)

```powershell
# Terminal 1 — ML
cd ml
python -m pip install -r requirements.txt
python -m uvicorn server:app --reload --port 8000

# Terminal 2 — Backend
npm run backend

# Terminal 3 — Frontend
npm run frontend
```

Open **http://localhost:5173**

## Deploy on Streamlit

**Guide:** [deploy/STREAMLIT.md](./deploy/STREAMLIT.md)

```powershell
pip install -r requirements.txt
streamlit run streamlit_app.py
```

On [Streamlit Cloud](https://share.streamlit.io/), set main file to `streamlit_app.py` and add model weights via **Git LFS** or `MODEL_URL` in Secrets.

## Deploy (Docker)

**Full guide:** [deploy/DEPLOY.md](./deploy/DEPLOY.md)

```powershell
# Requires ml/model.weights.h5 and Docker Desktop
docker compose up --build
```

Open **http://localhost:8080**

## Project layout

```
dataset/           # Your raw images (7 class folders)
dataset_split/     # Auto-generated train/val/test (gitignored)
ml/                # Model weights + FastAPI server
frontend/          # React dashboard
backend/           # Node.js API
notebooks/         # split_dataset.py, train_model.py, Colab notebook
deploy/            # Docker nginx + deployment docs
```

## Notes

- Small datasets (~20/class) limit accuracy; check `ml/training_report.json` for test metrics.
- Edit disease text in `ml/disease_info.json`.
- Predictions use **MobileNetV2** with proper preprocessing (no double scaling).
