"""
Train marigold disease model with proper train/val/test splits.

1. Run split first (once):  python notebooks/split_dataset.py
2. Train:                   python notebooks/train_model.py

Outputs in ml/:
  model.h5, class_indices.json, model_config.json, training_report.json
"""

import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import tensorflow as tf
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input

ROOT = Path(__file__).resolve().parent.parent
SPLIT_DIR = ROOT / "dataset_split"
ML_DIR = ROOT / "ml"
OUTPUT_MODEL = ML_DIR / "model.weights.h5"
OUTPUT_CONFIG = ML_DIR / "model_config.json"
OUTPUT_INDICES = ML_DIR / "class_indices.json"
OUTPUT_REPORT = ML_DIR / "training_report.json"
BEST_WEIGHTS = ML_DIR / "best_weights.weights.h5"

IMG_SIZE = (224, 224)
BATCH_SIZE = 8
SEED = 42
CLASS_NAMES = [
    "Healthy",
    "Leaf spot",
    "Bud rot",
    "Botrytis blight",
    "Foliage blight",
    "Stem rot",
    "White mold",
]


def ensure_split():
    if SPLIT_DIR.exists() and (SPLIT_DIR / "train").exists():
        return
    print("Creating dataset_split (train/val/test)...")
    subprocess.check_call([sys.executable, str(ROOT / "notebooks" / "split_dataset.py")])


def make_generators():
    train_aug = ImageDataGenerator(
        preprocessing_function=preprocess_input,
        rotation_range=30,
        zoom_range=0.25,
        width_shift_range=0.2,
        height_shift_range=0.2,
        horizontal_flip=True,
        brightness_range=(0.8, 1.2),
    )
    eval_gen = ImageDataGenerator(preprocessing_function=preprocess_input)

    kw = dict(
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode="categorical",
        classes=CLASS_NAMES,
        seed=SEED,
    )

    train_gen = train_aug.flow_from_directory(SPLIT_DIR / "train", shuffle=True, **kw)
    val_gen = eval_gen.flow_from_directory(SPLIT_DIR / "val", shuffle=False, **kw)
    test_gen = eval_gen.flow_from_directory(SPLIT_DIR / "test", shuffle=False, **kw)
    return train_gen, val_gen, test_gen


def evaluate(model, generator, name: str) -> dict:
    generator.reset()
    loss, acc = model.evaluate(generator, verbose=0)
    generator.reset()
    preds = model.predict(generator, verbose=0)
    y_true = generator.classes
    y_pred = np.argmax(preds, axis=1)
    per_class = {}
    for i, cname in enumerate(CLASS_NAMES):
        mask = y_true == i
        if mask.sum() == 0:
            continue
        per_class[cname] = {
            "samples": int(mask.sum()),
            "accuracy": float((y_pred[mask] == y_true[mask]).mean()),
        }
    return {"split": name, "loss": float(loss), "accuracy": float(acc), "per_class": per_class}


def save_artifacts(class_indices: dict, report: dict):
    ML_DIR.mkdir(parents=True, exist_ok=True)
    index_to_name = {str(v): k for k, v in class_indices.items()}
    with open(OUTPUT_INDICES, "w", encoding="utf-8") as f:
        json.dump(index_to_name, f, indent=2)
    config = {
        "architecture": "mobilenet_v2",
        "img_size": list(IMG_SIZE),
        "preprocessing": "mobilenet_v2",
        "class_names": CLASS_NAMES,
    }
    with open(OUTPUT_CONFIG, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)
    with open(OUTPUT_REPORT, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)


def main():
    ensure_split()
    if not SPLIT_DIR.exists():
        raise SystemExit("dataset_split not found. Run: python notebooks/split_dataset.py")

    tf.random.set_seed(SEED)
    train_gen, val_gen, test_gen = make_generators()
    print("Class indices:", train_gen.class_indices)

    sys.path.insert(0, str(ML_DIR))
    from model_factory import build_mobilenet_model

    phase1_callbacks = [
        EarlyStopping(monitor="val_accuracy", patience=6, restore_best_weights=True, mode="max"),
        ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=3, min_lr=1e-6),
    ]

    if BEST_WEIGHTS.exists():
        BEST_WEIGHTS.unlink()

    # Phase 1 — frozen MobileNetV2 base
    model, base = build_mobilenet_model(len(CLASS_NAMES), trainable_base=False)
    model.fit(train_gen, validation_data=val_gen, epochs=30, callbacks=phase1_callbacks)

    # Phase 2 — fine-tune top layers (new callbacks; do not reload phase-1 checkpoint)
    base.trainable = True
    for layer in base.layers[:-30]:
        layer.trainable = False
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-5),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )
    phase2_callbacks = [
        EarlyStopping(monitor="val_accuracy", patience=5, restore_best_weights=True, mode="max"),
        ModelCheckpoint(str(BEST_WEIGHTS), monitor="val_accuracy", save_best_only=True, mode="max"),
    ]
    model.fit(train_gen, validation_data=val_gen, epochs=15, callbacks=phase2_callbacks)

    report = {
        "train": evaluate(model, train_gen, "train"),
        "validation": evaluate(model, val_gen, "validation"),
        "test": evaluate(model, test_gen, "test"),
    }
    print("\n=== Test accuracy:", round(report["test"]["accuracy"] * 100, 1), "% ===")
    print(json.dumps(report["test"]["per_class"], indent=2))

    model.save_weights(str(OUTPUT_MODEL))
    save_artifacts(train_gen.class_indices, report)
    print(f"\nSaved weights: {OUTPUT_MODEL}")
    print(f"Saved class map: {OUTPUT_INDICES}")
    print(f"Saved report:    {OUTPUT_REPORT}")


if __name__ == "__main__":
    main()
