# Colab training (updated pipeline)

## 1. On your PC (once)

```powershell
cd C:\disease-prediction
python notebooks\split_dataset.py
```

This creates `dataset_split/` with **train (70%)**, **val (15%)**, **test (15%)** per class.

Zip it: right-click `dataset_split` → Send to → Compressed folder → `dataset_split.zip`

## 2. In Colab

1. Upload `notebooks/train_model.ipynb` or copy cells from `train_model.py`
2. Runtime → GPU
3. Upload **`dataset_split.zip`**
4. Run all cells
5. Download from `ml/`:
   - `model.h5`
   - `class_indices.json`
   - `model_config.json`
   - `training_report.json`

## 3. Copy to project

Place all four files in `C:\disease-prediction\ml\`

## 4. Restart ML server

```powershell
cd C:\disease-prediction\ml
python -m uvicorn server:app --reload --port 8000
```

Check `training_report.json` for test accuracy per class.
