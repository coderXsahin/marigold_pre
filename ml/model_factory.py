"""Shared model build + preprocessing (training and inference must match)."""

import io

import numpy as np
from PIL import Image

IMG_SIZE = (224, 224)

CLASS_NAMES = [
    "Healthy",
    "Leaf spot",
    "Bud rot",
    "Botrytis blight",
    "Foliage blight",
    "Stem rot",
    "White mold",
]


def build_mobilenet_model(num_classes: int, trainable_base: bool = False):
    from tensorflow.keras import layers, models
    from tensorflow.keras.applications import MobileNetV2

    base = MobileNetV2(
        weights="imagenet",
        include_top=False,
        input_shape=(*IMG_SIZE, 3),
    )
    base.trainable = trainable_base

    inputs = layers.Input(shape=(*IMG_SIZE, 3))
    x = base(inputs, training=False)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dropout(0.35)(x)
    x = layers.Dense(128, activation="relu")(x)
    x = layers.Dropout(0.35)(x)
    outputs = layers.Dense(num_classes, activation="softmax")(x)
    model = models.Model(inputs, outputs)
    model.compile(
        optimizer="adam",
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model, base


def preprocess_pil_image(img: Image.Image) -> np.ndarray:
    """MobileNetV2 preprocess: RGB 0-255 -> model input batch."""
    from tensorflow.keras.applications.mobilenet_v2 import preprocess_input

    img = img.convert("RGB").resize(IMG_SIZE)
    arr = np.array(img, dtype=np.float32)
    return np.expand_dims(preprocess_input(arr), axis=0)


def preprocess_bytes(image_bytes: bytes) -> np.ndarray:
    return preprocess_pil_image(Image.open(io.BytesIO(image_bytes)))
