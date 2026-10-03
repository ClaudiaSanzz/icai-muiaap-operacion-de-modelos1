"""TODO: transformación de una muestra validada en el vector del modelo."""

from dataclasses import dataclass

from model_inference.contracts import WineQualityRequest


# Este contrato se entrega ya decidido: no cambies ni los nombres ni el orden.
FEATURE_NAMES = (
    "fixed_acidity",
    "volatile_acidity",
    "citric_acid",
    "residual_sugar",
    "chlorides",
    "free_sulfur_dioxide",
    "total_sulfur_dioxide",
    "density",
    "ph",
    "sulphates",
    "alcohol",
)

PREPROCESSING_VERSION = "v1"


@dataclass(frozen=True, slots=True)
class WineFeatures:
    values: list[float]


def preprocess_wine_request(request: WineQualityRequest) -> WineFeatures:
    values = []

    for name in FEATURE_NAMES:
        value = getattr(request, name)
        values.append(value)

    return WineFeatures(values=values)

# Implementa WineFeatures y preprocess_wine_request(). El orden anterior debe
# coincidir con el artefacto, no con un orden arbitrario del CSV.
