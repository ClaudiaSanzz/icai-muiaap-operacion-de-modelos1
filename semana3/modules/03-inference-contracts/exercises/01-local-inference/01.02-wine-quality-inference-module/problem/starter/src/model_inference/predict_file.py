"""TODO: script CLI que encadena contratos, preprocesado e inferencia."""

# Implementa el comando:
# python -m model_inference.predict_file --input <csv> --output <csv>
# No dejes un archivo de salida parcial si alguna fila es inválida.
"""Script CLI que encadena contratos, preprocesado e inferencia."""

import argparse
import csv
from pathlib import Path

from model_inference.contracts import WineQualityRequest
from model_inference.preprocess import preprocess_wine_request
from model_inference.inference import load_wine_quality_model, infer_wine_quality


def predict_file(input_path: Path, output_path: Path):
    artifact = load_wine_quality_model()

    predictions = []

    with input_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            sample_id = row.pop("sample_id")

            request = WineQualityRequest.model_validate(row)

            features = preprocess_wine_request(request)

            prediction = infer_wine_quality(
                sample_id,
                features,
                artifact,
            )

            predictions.append(prediction)

    with output_path.open("w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "sample_id",
            "predicted_class",
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

    args = parser.parse_args()

    predict_file(
        Path(args.input),
        Path(args.output),
    )


if __name__ == "__main__":
    main()