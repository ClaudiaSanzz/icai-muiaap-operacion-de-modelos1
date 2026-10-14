"""Script CLI que encadena contratos, preprocesado e inferencia."""

import argparse
import csv
from pathlib import Path

from model_inference.contracts import WineQualityPrediction, WineQualityRequest
from model_inference.inference import (
    DEFAULT_MODEL_PATH,
    infer_wine_quality,
    load_wine_quality_model,
)
from model_inference.preprocess import PREPROCESSING_VERSION, preprocess_wine_request


def predict_file(
    input_path: Path, output_path: Path, model_path: Path = DEFAULT_MODEL_PATH
):

    model = load_wine_quality_model(model_path)

    predictions = []

    with input_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            sample_id = row.pop("sample_id")
            if not sample_id:
                raise ValueError("sample_id no puede estar vacío")

            try:
                request = WineQualityRequest.model_validate(row)
            except ValueError as error:
                raise ValueError(f"Error en la muestra {sample_id}: {error}") from error

            features = preprocess_wine_request(request)
            quality_band, confidence = infer_wine_quality(model, features)
            prediction = WineQualityPrediction(
                sample_id=sample_id,
                quality_band=quality_band,
                confidence=confidence,
                model_version=model.model_version,
                preprocessing_version=PREPROCESSING_VERSION,
            )

            predictions.append(prediction)

    with output_path.open("w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "sample_id",
            "quality_band",
            "confidence",
            "model_version",
            "preprocessing_version",
        ]

        writer = csv.DictWriter(f, fieldnames=fieldnames)

        writer.writeheader()

        for prediction in predictions:
            writer.writerow(prediction.model_dump())


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--model", default=str(DEFAULT_MODEL_PATH))

    args = parser.parse_args()

    try:
        predict_file(
            Path(args.input),
            Path(args.output),
            Path(args.model),
        )

    except (ValueError, FileNotFoundError, KeyError) as error:
        parser.exit(2, f"Error: {error}\n")


if __name__ == "__main__":
    main()
