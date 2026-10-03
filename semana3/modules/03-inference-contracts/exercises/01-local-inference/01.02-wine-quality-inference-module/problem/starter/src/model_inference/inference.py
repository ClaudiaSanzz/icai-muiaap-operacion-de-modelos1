"""TODO: carga del .joblib e inferencia sobre características preparadas."""

# Declara DEFAULT_MODEL_PATH, load_wine_quality_model() e infer_wine_quality().
# Comprueba las características del artefacto antes de llamar al clasificador.

"""Carga del .joblib e inferencia sobre características preparadas."""

from pathlib import Path

import joblib

from model_inference.contracts import WineQualityPrediction
from model_inference.preprocess import (
    FEATURE_NAMES,
    WineFeatures,
    PREPROCESSING_VERSION,
)


DEFAULT_MODEL_PATH = Path("../assets/wine_quality_classifier.joblib")


def load_wine_quality_model(path: Path = DEFAULT_MODEL_PATH):
    artifact = joblib.load(path)

    if not isinstance(artifact, dict):
        raise ValueError("El artefacto debe ser un diccionario")

    if "estimator" not in artifact:
        raise ValueError("El artefacto no contiene estimator")

    if "feature_names" not in artifact:
        raise ValueError("El artefacto no contiene feature_names")

    if tuple(artifact["feature_names"]) != FEATURE_NAMES:
        raise ValueError("Las características del artefacto no coinciden con FEATURE_NAMES")

    if "model_version" not in artifact:
        raise ValueError("El artefacto no contiene model_version")

    return artifact


def infer_wine_quality(sample_id: str, features: WineFeatures, artifact) -> WineQualityPrediction:
    estimator = artifact["estimator"]

    if len(features.values) != len(FEATURE_NAMES):
        raise ValueError("El vector debe contener 11 características")

    prediction = estimator.predict([features.values])[0]

    probabilities = estimator.predict_proba([features.values])[0]
    confidence = float(max(probabilities))

    result = WineQualityPrediction(
        sample_id=sample_id,
        predicted_class=str(prediction),
        confidence=confidence,
        model_version=str(artifact["model_version"]),
        preprocessing_version=PREPROCESSING_VERSION,
    )

    return result