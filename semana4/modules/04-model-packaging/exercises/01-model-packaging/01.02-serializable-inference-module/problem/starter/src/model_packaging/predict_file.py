"""Punto de extensión del CLI de inferencia sobre un bundle."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from model_packaging.artifact import (
    DEFAULT_BUNDLE_PATH,
    infer_wine_quality,
    load_model_bundle,
)
from model_packaging.contracts import WineQualityRequest


def predict_file(
    input_path: Path,
    output_path: Path,
    bundle_path: Path,
) -> int:
    """TODO: valida todas las filas y escribe el CSV solo al final."""
    # cargo el modelo y su manifiesto
    bundle = load_model_bundle(bundle_path)

    # aqui leo el csv
    with input_path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        rows = list(reader)

    resultados = []

    # recorro todas las filas del csv
    for row in rows:
        sample_id = row.pop("sample_id")  # guarda el idetificador del vino
        request = WineQualityRequest(**row)  # validar los datos de entrada
        prediction = infer_wine_quality(bundle, request)
        resultados.append(
            {
                "sample_id": sample_id,
                "predicted_class": prediction.quality_band,
                "confidence": prediction.confidence,
                "model_version": prediction.model_version,
                "preprocessing_version": prediction.preprocessing_version,
            }
        )

    # creo la carpeta de salida si no existe
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Guardar las predicciones cuando todas sean válidas
    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "sample_id",
                "predicted_class",
                "confidence",
                "model_version",
                "preprocessing_version",
            ],
        )

        writer.writeheader()
        writer.writerows(resultados)

    print(f"Se han guardado {len(resultados)} predicciones en {output_path}")

    return len(resultados)


def parse_args() -> argparse.Namespace:
    """Declara la interfaz del comando público."""

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--bundle", default=DEFAULT_BUNDLE_PATH, type=Path)
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    raise SystemExit(
        predict_file(
            input_path=arguments.input,
            output_path=arguments.output,
            bundle_path=arguments.bundle,
        )
    )
