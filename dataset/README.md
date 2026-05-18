# Dataset

Place marigold images in the class folders below. **JPG and PNG only**, ideally under 100 KB per image (per PRD).

| Folder            | Class label              |
|-------------------|--------------------------|
| `Healthy/`        | Marigold – Healthy       |
| `Leaf spot/`      | Marigold – Leaf spot     |
| `Bud rot/`        | Marigold – Bud rot       |
| `Botrytis blight/`| Marigold – Botrytis blight |
| `Foliage blight/` | Marigold – Foliage blight |
| `Stem rot/`       | Marigold – Stem rot      |
| `White mold/`     | Marigold – White mold    |

Minimum **2–5 images per class** to start; add more for better accuracy.

After adding images, train the model:

```bash
python notebooks/train_model.py
```
