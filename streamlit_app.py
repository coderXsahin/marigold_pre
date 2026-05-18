"""Marigold disease detection — Streamlit UI (Streamlit Community Cloud)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import streamlit as st
from PIL import Image

ROOT = Path(__file__).resolve().parent
ML_DIR = ROOT / "ml"
sys.path.insert(0, str(ML_DIR))

from model_factory import (  # noqa: E402
    build_mobilenet_model,
    preprocess_pil_image,
)

CONFIDENCE_THRESHOLD = 0.50
MODEL_PATH = ML_DIR / "model.weights.h5"
LEGACY_MODEL_PATH = ML_DIR / "model.h5"
CLASS_INDICES_PATH = ML_DIR / "class_indices.json"
DISEASE_INFO_PATH = ML_DIR / "disease_info.json"


def format_disease_name(folder_name: str) -> str:
    return f"Marigold – {folder_name}"


def load_class_labels() -> list[str]:
    if CLASS_INDICES_PATH.exists():
        with open(CLASS_INDICES_PATH, encoding="utf-8") as f:
            indices = json.load(f)
        return [indices[str(i)] for i in range(len(indices))]
    from model_factory import CLASS_NAMES

    return list(CLASS_NAMES)


def load_disease_info() -> dict[str, str]:
    if DISEASE_INFO_PATH.exists():
        with open(DISEASE_INFO_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {}


def resolve_weights_path() -> Path | None:
    if MODEL_PATH.exists():
        return MODEL_PATH
    if LEGACY_MODEL_PATH.exists():
        return LEGACY_MODEL_PATH
    return None


def maybe_download_weights() -> Path | None:
    """Optional: set MODEL_URL in Streamlit secrets to fetch weights on deploy."""
    try:
        url = st.secrets.get("MODEL_URL")
    except Exception:
        url = None
    if not url:
        return None

    target = MODEL_PATH
    if target.exists():
        return target

    import urllib.request

    target.parent.mkdir(parents=True, exist_ok=True)
    with st.spinner("Downloading model weights…"):
        urllib.request.urlretrieve(url, target)
    return target if target.exists() else None


@st.cache_resource(show_spinner="Loading MobileNetV2 model…")
def get_model():
    maybe_download_weights()
    weights_path = resolve_weights_path()
    if weights_path is None:
        return None, load_class_labels(), load_disease_info()

    class_labels = load_class_labels()
    model, _ = build_mobilenet_model(len(class_labels), trainable_base=False)
    model.load_weights(str(weights_path))
    return model, class_labels, load_disease_info()


def interpret_prediction(
    probs: np.ndarray,
    class_labels: list[str],
    disease_info: dict[str, str],
) -> dict:
    idx = int(np.argmax(probs))
    confidence = float(probs[idx])
    class_name = class_labels[idx]

    if confidence < CONFIDENCE_THRESHOLD:
        return {
            "is_healthy": True,
            "disease_name": format_disease_name("Healthy"),
            "confidence": confidence,
            "note": "Low confidence — classified as Healthy per threshold",
        }

    if class_name == "Healthy":
        return {
            "is_healthy": True,
            "disease_name": format_disease_name("Healthy"),
            "confidence": confidence,
        }

    return {
        "is_healthy": False,
        "disease_name": format_disease_name(class_name),
        "confidence": confidence,
        "details": disease_info.get(class_name, "No description configured."),
        "class_name": class_name,
    }


def main():
    st.set_page_config(
        page_title="Marigold Disease Detection",
        page_icon="🌼",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.markdown(
        """
        <style>
        .block-container { padding-top: 1.5rem; max-width: 1100px; }
        [data-testid="stSidebar"] { background: linear-gradient(180deg, #143d30 0%, #1b5e4a 100%); }
        [data-testid="stSidebar"] * { color: #e8f5ec !important; }
        .result-healthy {
            padding: 1rem 1.25rem; border-radius: 12px;
            background: #e8f5ec; border: 1px solid #2e7d4a; margin: 1rem 0;
        }
        .result-diseased {
            padding: 1rem 1.25rem; border-radius: 12px;
            background: #fdecea; border: 1px solid #c0392b; margin: 1rem 0;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.title("Marigold Health")
        st.caption("Plant disease AI")
        st.divider()
        st.markdown("**Classes detected**")
        for label in load_class_labels():
            st.markdown(f"· {label}")

    st.title("Marigold disease detection")
    st.markdown("Upload a marigold leaf or plant photo to classify health and common diseases.")

    model, class_labels, disease_info = get_model()

    if model is None:
        st.error(
            "Model weights not found. For Streamlit Cloud, either:\n\n"
            "1. Add `ml/model.weights.h5` with **Git LFS**, or\n"
            "2. Set `MODEL_URL` in app **Secrets** to a direct download link.\n\n"
            "See [deploy/STREAMLIT.md](https://github.com/coderXsahin/marigold_pre/blob/main/deploy/STREAMLIT.md)."
        )
        st.stop()

    col_upload, col_result = st.columns([1, 1], gap="large")

    with col_upload:
        st.subheader("Upload image")
        uploaded = st.file_uploader(
            "JPG or PNG",
            type=["jpg", "jpeg", "png"],
            label_visibility="collapsed",
        )
        if uploaded:
            image = Image.open(uploaded)
            st.image(image, use_container_width=True, caption="Uploaded image")

    with col_result:
        st.subheader("Diagnosis")
        if uploaded is None:
            st.info("Upload an image to run analysis.")
        else:
            with st.spinner("Analyzing…"):
                batch = preprocess_pil_image(image)
                probs = model.predict(batch, verbose=0)[0]
                result = interpret_prediction(probs, class_labels, disease_info)

            pct = round(result["confidence"] * 100)
            if result["is_healthy"]:
                st.markdown(
                    f'<div class="result-healthy">'
                    f"<strong>Healthy</strong><br>{result['disease_name']}<br>"
                    f"Confidence: <strong>{pct}%</strong>"
                    f"</div>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f'<div class="result-diseased">'
                    f"<strong>Disease detected</strong><br>{result['disease_name']}<br>"
                    f"Confidence: <strong>{pct}%</strong>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

            if result.get("note"):
                st.caption(result["note"])
            if result.get("details"):
                st.markdown("**About this condition**")
                st.write(result["details"])

            st.markdown("**Class probabilities**")
            chart_data = {
                class_labels[i]: float(probs[i]) * 100
                for i in range(len(class_labels))
            }
            st.bar_chart(chart_data)


if __name__ == "__main__":
    main()
