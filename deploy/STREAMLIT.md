# Deploy on Streamlit Community Cloud

Streamlit runs **only the Python ML app** (no Node backend). History and the React UI are not included.

## 1. Push code to GitHub

Repo: https://github.com/coderXsahin/marigold_pre

Required in the repo:

- `streamlit_app.py` (entry point)
- `requirements.txt` (root)
- `ml/model_factory.py`, `ml/class_indices.json`, `ml/disease_info.json`

## 2. Provide model weights (required)

Weights are gitignored locally. Pick **one** option:

### Option A — Git LFS (recommended)

```powershell
cd e:\disease-prediction
git lfs install
git lfs track "ml/model.weights.h5"
git add .gitattributes ml/model.weights.h5
git commit -m "Add model weights via Git LFS"
git push
```

### Option B — Secrets download URL

1. Upload `model.weights.h5` to Google Drive, Hugging Face, or a GitHub Release.
2. Get a **direct download** URL.
3. In Streamlit Cloud → your app → **Settings → Secrets**:

```toml
MODEL_URL = "https://your-direct-link-to/model.weights.h5"
```

The app downloads the file on first run.

## 3. Deploy on Streamlit Cloud

1. Go to https://share.streamlit.io/
2. Sign in with GitHub.
3. **New app** → select `coderXsahin/marigold_pre`.
4. Set:
   - **Main file path:** `streamlit_app.py`
   - **Branch:** `main`
5. Under **Advanced settings**, set **Python version** to **3.11** (required for TensorFlow).
6. Click **Deploy** (first build may take 5–15 minutes because of TensorFlow).

If you see `installer returned a non-zero exit code`, use **Manage app → Reboot** after pulling the latest `environment.yml` fix.

## 4. Test locally first

```powershell
cd e:\disease-prediction
python -m pip install -r requirements.txt
streamlit run streamlit_app.py
```

Open http://localhost:8501

## Limits

- Free tier: app sleeps when idle; cold start can be slow.
- TensorFlow needs ~1–2 GB RAM; very large models may fail on free tier.
- Max upload size: 10 MB (see `.streamlit/config.toml`).

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `Model weights not found` | Use Git LFS or `MODEL_URL` secret |
| Build timeout | Retry deploy; TensorFlow install is heavy |
| `ModuleNotFoundError: model_factory` | Ensure `ml/` folder is in the repo |
| Wrong predictions | Confirm `class_indices.json` matches training |
