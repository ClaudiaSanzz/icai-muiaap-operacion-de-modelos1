"""Puntos de extensión del taller de serialización."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

import joblib
from pydantic import BaseModel, ConfigDict, Field, model_validator

from model_packaging.contracts import (
    QualityBand,
    WineQualityPrediction,
    WineQualityRequest,
)
from model_packaging.preprocess import (
    FEATURE_NAMES,
    PREPROCESSING_VERSION,
    preprocess_wine_request,
)

ARTIFACT_SCHEMA_VERSION = "wine-quality-bundle-v1"
DEFAULT_BUNDLE_PATH = Path("models/wine_quality_bundle")
MANIFEST_FILENAME = "manifest.json"
MODEL_FILENAME = "model.joblib"
# Los elementos deben ser de tipo QualityBand.
# Los tres puntos (...) indican que puede haber
# cualquier número de elementos.
OUTPUT_LABELS: tuple[QualityBand, ...] = (
    "needs_review",
    "acceptable",
    "excellent",
)


# define las funciones que debe tener el estimador
class WineQualityEstimator(Protocol):
    """Interfaz mínima que debe cumplir el estimador cargado."""

    def predict(self, features: list[list[float]]) -> Sequence[str]:
        """Devuelve una etiqueta por fila."""

    def predict_proba(self, features: list[list[float]]) -> Sequence[Sequence[float]]:
        """Devuelve probabilidades por fila."""


# define los 6 campos obligatorios del manifiesto.
class ArtifactManifest(BaseModel):
    """TODO: declara y valida los metadatos del bundle."""

    model_config = ConfigDict(extra="forbid")

    schema_version: str
    model_version: str = Field(min_length=1)
    preprocessing_version: str
    feature_names: tuple[str, ...]
    output_labels: tuple[QualityBand, ...]
    estimator_type: str = Field(min_length=1)

    @model_validator(mode="after")
    def validate_contract(self):  # self representa a manifest
        if (
            self.feature_names != FEATURE_NAMES
        ):  # self.feature_names son las features guardadas en manifest
            raise ValueError("El orden o los nombres de las features no coinciden")

        if self.output_labels != OUTPUT_LABELS:
            raise ValueError("Las etiquetas de salida no coinciden")

        return self


# agrupa el estiamdor cargado y su manifiesto
@dataclass(frozen=True)
class LoadedModelBundle:
    """Bundle cargado; no modificar esta interfaz pública."""

    estimator: WineQualityEstimator
    manifest: ArtifactManifest


# crea el manifiesto del modelo
def create_manifest(
    estimator: WineQualityEstimator, model_version: str
) -> ArtifactManifest:
    """TODO: devuelve un manifiesto compatible con el contrato."""

    return ArtifactManifest(
        schema_version=ARTIFACT_SCHEMA_VERSION,
        model_version=model_version,
        preprocessing_version=PREPROCESSING_VERSION,
        feature_names=FEATURE_NAMES,
        output_labels=OUTPUT_LABELS,
        estimator_type=type(estimator).__name__,
    )

# getattr busca el atributo predict y devuelve None si no existe.
# callable comprueba si el atributo encontrado se puede ejecutar.
# Si el modelo no tiene un método predict ejecutable, lanza un error.


def validar_estimador(estimator):
    if not callable(getattr(estimator, "predict", None)):
        raise ValueError("El modelo no tiene predict")

    if not callable(getattr(estimator, "predict_proba", None)):
        raise ValueError("El modelo no tiene predict_proba")


def save_model_bundle(
    bundle_path: Path,
    estimator: WineQualityEstimator,
    manifest: ArtifactManifest | None = None,
) -> ArtifactManifest:
    """TODO: escribe manifest.json y model.joblib de forma segura."""
    # compruebo que el modelo tiene los metodos necesarios
    validar_estimador(estimator)
    # creo el manifiesto si no existe
    if manifest is None:
        manifest = create_manifest(estimator, "unknown")

    # compruebo las features
    if manifest.feature_names != FEATURE_NAMES:
        raise ValueError("las features no coinciden")

    # compruebo el tipo de estimador
    if manifest.estimator_type != type(estimator).__name__:
        raise ValueError("el tipo de estimador no coincide")

    # crea la carpeta
    bundle_path = Path(bundle_path)
    bundle_path.mkdir(parents=True, exist_ok=True)

    # guardamos el modelo
    model_path = bundle_path / MODEL_FILENAME
    joblib.dump(
        {"estimator": estimator}, model_path, compress=3
    )  # compress es cuanto queremos comprimri el archivo

    # guardar el manifiesto
    manifest_path = bundle_path / MANIFEST_FILENAME
    manifest_path.write_text(
        manifest.model_dump_json(
            indent=2
        ),  # indent es para que se vea el json vertical
        encoding="utf-8",
    )
    return manifest


# carfa el modelo y valida su manifiesto
def load_model_bundle(bundle_path: Path) -> LoadedModelBundle:
    """TODO: valida el manifiesto antes de cargar el estimador."""
    # ruta de los archivos
    manifest_path = bundle_path / MANIFEST_FILENAME
    model_path = bundle_path / MODEL_FILENAME

    # compruebo que existen los archivos
    if not manifest_path.is_file() or not model_path.is_file():
        raise FileNotFoundError("Falta manifest.json o model.joblib")

    # leemos y validamos el manifiesto
    manifest = ArtifactManifest.model_validate_json(
        manifest_path.read_text(encoding="utf-8")
    )

    # cargamos el modelo
    payload = joblib.load(model_path)

    # comprobar que es un diccionario
    if not isinstance(payload, dict):
        raise ValueError("EL modelo debe estar en un diccionario")

    # obtener el estimador
    estimator = payload.get("estimator")

    # comprobar que el estimador es valido
    validar_estimador(estimator)

    # comprobar que coincide con el manifiesto
    if manifest.estimator_type != type(estimator).__name__:
        raise ValueError("El tipo de estimador no coincide")

    # devolver el modelo y su manifiesto
    return LoadedModelBundle(estimator=estimator, manifest=manifest)


# Recibe los datos de un vino, los pasa al modelo
# y devuelve una predicción válida.
def infer_wine_quality(
    bundle: LoadedModelBundle,
    request: WineQualityRequest,
) -> WineQualityPrediction:
    """TODO: preprocesa, invoca el estimador y valida la respuesta."""

    # preprocesar los datos
    features = preprocess_wine_request(request)
    matrix = [features.as_vector()]

    # hacer la prediccion
    etiquetas = bundle.estimator.predict(matrix)
    probabilidades = bundle.estimator.predict_proba(matrix)

    # comrpobar que tenemos una prediccion por fila
    if len(etiquetas) != 1 or len(probabilidades) != 1:
        raise ValueError("El modelo debe devolver una prediccion pro fila")

    # comprobamos las probabilidades
    if len(probabilidades[0]) == 0:
        raise ValueError("El modelo no ha devuelto probabilidades")

    # obtener la etiqueta y la confianza
    etiqueta = str(etiquetas[0])
    confianza = max(float(p) for p in probabilidades[0])

    # crear y validar la respuesta
    resultado = WineQualityPrediction(
        quality_band=etiqueta,
        confidence=confianza,
        model_version=bundle.manifest.model_version,
        preprocessing_version=bundle.manifest.preprocessing_version,
    )

    return resultado
