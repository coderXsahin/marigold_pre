"""
Create stratified train / val / test folders from dataset/.

Usage:
  python notebooks/split_dataset.py

Output:
  dataset_split/train/<class>/
  dataset_split/val/<class>/
  dataset_split/test/<class>/
"""

import json
import random
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "dataset"
OUTPUT = ROOT / "dataset_split"
MANIFEST = OUTPUT / "split_manifest.json"

CLASS_NAMES = [
    "Healthy",
    "Leaf spot",
    "Bud rot",
    "Botrytis blight",
    "Foliage blight",
    "Stem rot",
    "White mold",
]

IMAGE_EXTS = {".jpg", ".jpeg", ".png"}
TRAIN_RATIO = 0.70
VAL_RATIO = 0.15
TEST_RATIO = 0.15
SEED = 42


def collect_images(class_dir: Path) -> list[Path]:
    return sorted(
        p for p in class_dir.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_EXTS
    )


def split_counts(n: int) -> tuple[int, int, int]:
    n_train = max(1, int(round(n * TRAIN_RATIO)))
    n_val = max(1, int(round(n * VAL_RATIO))) if n >= 3 else 0
    n_test = n - n_train - n_val
    if n_test < 1 and n >= 2:
        n_test = 1
        n_train = n - n_val - n_test
    return n_train, n_val, n_test


def main():
    if not SOURCE.exists():
        raise SystemExit(f"Source dataset not found: {SOURCE}")

    random.seed(SEED)
    manifest = {"seed": SEED, "ratios": {"train": TRAIN_RATIO, "val": VAL_RATIO, "test": TEST_RATIO}, "classes": {}}

    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)

    for split in ("train", "val", "test"):
        for name in CLASS_NAMES:
            (OUTPUT / split / name).mkdir(parents=True, exist_ok=True)

    for class_name in CLASS_NAMES:
        src_dir = SOURCE / class_name
        if not src_dir.exists():
            raise SystemExit(f"Missing class folder: {src_dir}")

        images = collect_images(src_dir)
        if len(images) < 2:
            raise SystemExit(f"Need at least 2 images in {class_name}, found {len(images)}")

        random.shuffle(images)
        n_train, n_val, n_test = split_counts(len(images))
        # Adjust if rounding left gaps
        while n_train + n_val + n_test > len(images):
            n_train -= 1
        while n_train + n_val + n_test < len(images):
            n_train += 1

        train_files = images[:n_train]
        val_files = images[n_train : n_train + n_val]
        test_files = images[n_train + n_val :]

        splits = {"train": train_files, "val": val_files, "test": test_files}
        manifest["classes"][class_name] = {k: [p.name for p in v] for k, v in splits.items()}

        for split_name, files in splits.items():
            for src in files:
                dst = OUTPUT / split_name / class_name / src.name
                shutil.copy2(src, dst)

        print(
            f"{class_name}: {len(images)} total -> "
            f"train {len(train_files)}, val {len(val_files)}, test {len(test_files)}"
        )

    with open(MANIFEST, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"\nSplit saved to {OUTPUT}")
    print(f"Manifest: {MANIFEST}")


if __name__ == "__main__":
    main()
