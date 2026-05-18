import io
import json
from contextlib import asynccontextmanager
from pathlib import Path

import numpy as np
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image

from model_factory import CLASS_NAMES, build_mobilenet_model, preprocess_pil_image

MODEL_PATH = Path(__file__).parent / "model.weights.h5"
LEGACY_MODEL_PATH = Path(__file__).parent / "model.h5"
MODEL_CONFIG_PATH = Path(__file__).parent / "model_config.json"
CLASS_INDICES_PATH = Path(__file__).parent / "class_indices.json"
DISEASE_INFO_PATH = Path(__file__).parent / "disease_info.json"
CONFIDENCE_THRESHOLD = 0.50

model = None
class_labels: list[str] = list(CLASS_NAMES)
disease_info: dict[str, str] = {}


def load_class_labels() -> list[str]:
    if CLASS_INDICES_PATH.exists():
        with open(CLASS_INDICES_PATH, encoding="utf-8") as f:
            indices = json.load(f)
        return [indices[str(i)] for i in range(len(indices))]
    return list(CLASS_NAMES)


def load_disease_info() -> dict[str, str]:
    if DISEASE_INFO_PATH.exists():
        with open(DISEASE_INFO_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {}


def format_disease_name(folder_name: str) -> str:
    return f"Marigold – {folder_name}"


def preprocess_image(image_bytes: bytes) -> np.ndarray:
    img = Image.open(io.BytesIO(image_bytes))
    return preprocess_pil_image(img)


def resolve_weights_path() -> Path:
    if MODEL_PATH.exists():
        return MODEL_PATH
    if LEGACY_MODEL_PATH.exists():
        return LEGACY_MODEL_PATH
    return MODEL_PATH


def load_trained_model(num_classes: int, weights_path: Path | None = None):
    path = weights_path or resolve_weights_path()
    m, _ = build_mobilenet_model(num_classes, trainable_base=False)
    m.load_weights(str(path))
    return m


def interpret_prediction(probs: np.ndarray) -> dict:
    idx = int(np.argmax(probs))
    confidence = float(probs[idx])
    class_name = class_labels[idx]

    if confidence < CONFIDENCE_THRESHOLD:
        return {
            "is_healthy": True,
            "disease_name": format_disease_name("Healthy"),
            "confidence": round(confidence, 4),
            "note": "Low confidence — classified as Healthy per threshold",
        }

    if class_name == "Healthy":
        return {
            "is_healthy": True,
            "disease_name": format_disease_name("Healthy"),
            "confidence": round(confidence, 4),
        }

    details = disease_info.get(class_name, "No description configured.")
    return {
        "is_healthy": False,
        "disease_name": format_disease_name(class_name),
        "confidence": round(confidence, 4),
        "details": details,
    }


@asynccontextmanager
async def lifespan(app: FastAPI):
    global model, disease_info, class_labels
    disease_info = load_disease_info()
    class_labels = load_class_labels()

    weights_path = resolve_weights_path()
    if not weights_path.exists():
        print(f"WARNING: Model not found at {MODEL_PATH} or {LEGACY_MODEL_PATH}")
        yield
        return

    try:
        model = load_trained_model(len(class_labels), weights_path)
        print(f"Model loaded: {weights_path}")
        print(f"Classes: {class_labels}")
    except Exception as e:
        print(f"ERROR loading model: {e}")
        raise

    yield


app = FastAPI(title="Marigold Disease Detection", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    report_path = Path(__file__).parent / "training_report.json"
    report = None
    if report_path.exists():
        with open(report_path, encoding="utf-8") as f:
            report = json.load(f)
    return {
        "status": "ok",
        "model_loaded": model is not None,
        "classes": class_labels,
        "test_accuracy": report.get("test", {}).get("accuracy") if report else None,
    }


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    if model is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Run notebooks/train_model.py or Colab training.",
        )

    if file.content_type not in ("image/jpeg", "image/png", "image/jpg"):
        raise HTTPException(status_code=400, detail="Only JPG and PNG images are allowed")

    contents = await file.read()
    batch = preprocess_image(contents)
    probs = model.predict(batch, verbose=0)[0]
    return interpret_prediction(probs)
