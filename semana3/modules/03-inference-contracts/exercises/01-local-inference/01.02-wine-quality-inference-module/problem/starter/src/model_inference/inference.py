"""Carga del .joblib e inferencia sobre características preparadas."""

from dataclasses import dataclass
from pathlib import Path

import joblib

from model_inference.preprocess import (
    FEATURE_NAMES,
    WineFeatures,
)

DEFAULT_MODEL_PATH = Path(__file__).resolve().parents[2] / "assets/wine_quality_classifier.joblib"

@dataclass
class LoadedWineModel:
    estimator: object
    model_version: str


def load_wine_quality_model(path: Path = DEFAULT_MODEL_PATH):
    artifact = joblib.load(path)

    if not isinstance(artifact, dict):
        raise ValueError("El artefacto debe ser un diccionario")

    if "estimator" not in artifact:
        raise ValueError("El artefacto no contiene un clasificador compatible")

    if "feature_names" not in artifact:
        raise ValueError("El artefacto no contiene feature_names")

    if tuple(artifact["feature_names"]) != FEATURE_NAMES:
        raise ValueError("Los feature_names no coinciden")

    if "model_version" not in artifact:
        raise ValueError("El artefacto no contiene model_version")

    estimator = artifact["estimator"]

    if not hasattr(estimator, "predict") or not hasattr(estimator, "predict_proba"):
        raise ValueError("El artefacto no contiene un clasificador compatible")

    return LoadedWineModel(estimator=estimator, model_version=artifact["model_version"])


def infer_wine_quality(
    model: LoadedWineModel, features: WineFeatures
) -> tuple[str, float]:

    vector = [features.as_vector()]

    prediction = model.estimator.predict(vector)[0]
    probabilities = model.estimator.predict_proba(vector)[0]

    confidence = round(float(max(probabilities)), 2)

    return str(prediction), confidence
