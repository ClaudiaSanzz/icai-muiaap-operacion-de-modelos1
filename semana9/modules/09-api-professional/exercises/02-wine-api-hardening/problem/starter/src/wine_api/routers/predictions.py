from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Body

from wine_api.dependencies import PredictorDep, RequestIdDep
from wine_api.schemas import (
    VALID_FEATURES_EXAMPLE,
    ErrorResponse,
    Prediction,
    PredictionRequest,
    PredictionResponse,
)

# TODO S9.3a: mueve aquí `prefix="/v1/predictions"` y `tags=["predictions"]`.
# TODO S9.3c: declara a nivel de router `responses=` para 400, 422 y 503 con
# `{"model": ErrorResponse, "description": ...}`. Así el 422 deja de
# documentarse como `HTTPValidationError`, que ya no es lo que devolvemos.
router = APIRouter(
    prefix="/v1/predictions",
    tags=["predictions"],
    responses={
        # le inidica a fastapi de que cuando se docuemnte un error 422, debe mostrar el
        # esquema de errorresponse
        400: {
            "model": ErrorResponse,
            "description": "Invalid JSON",
        },
        422: {
            "model": ErrorResponse,
            "description": "Validation error",
        },
        503: {
            "model": ErrorResponse,
            "description": "Prediction model unavailable",
        },
    },
)

# lo hemos cambiado porque
# tags: agrupa los endpoints por categorias dentro de Swagger
# prefix: establece una ruta comun para todos los endpoints de ese router

EXAMPLES = {
    "valid": {
        "summary": "Valid wine",
        "value": {"features": VALID_FEATURES_EXAMPLE},
    },
    "invalid_alcohol": {
        "summary": "Alcohol out of range",
        "value": {
            "features": {**VALID_FEATURES_EXAMPLE, "alcohol": 30},
        },
    },
    "missing_alcohol": {
        "summary": "Missing alcohol",
        "value": {
            "features": {
                k: v for k, v in VALID_FEATURES_EXAMPLE.items() if k != "alcohol"
            },
        },
    },
}


# predice la calidad de un vino a partir de 11 caracterisitcas

# recibe las variables fisicoquimicas del vino, que deben cumplir
# los rangos definidos en WineFeatures.
# Devuelve la clasificacion, la confianza redondeada a dos decimales
# y las versiones del modelo y del preprocesamiento.


@router.post(
    "",
    summary="Predict wine quality",
    response_description="Wine quality prediction with confidence and model versions",
)
def create_prediction(
    payload: Annotated[
        PredictionRequest,
        Body(openapi_examples=EXAMPLES),
    ],
    predictor: PredictorDep,
    request_id: RequestIdDep,
) -> PredictionResponse:  # indicamos que la funcion devuelve ese modelo de pydantic
    """Predice la calidad de un vino a partir de 11 características.

    Las variables deben cumplir los rangos definidos en WineFeatures.
    Devuelve la clasificación, la confianza con dos decimales
    y las versiones del modelo y del preprocesamiento.
    """

    # TODO S9.3e: añade summary, response_description y un docstring útil para
    # quien consume la API (campos, rangos, decimales de confidence).
    # TODO S9.3f: ofrece en Swagger al menos tres ejemplos de cuerpo (uno válido
    # y dos inválidos). Investiga `Annotated[PredictionRequest, Body(...)]` con
    # `openapi_examples=`; usa VALID_FEATURES_EXAMPLE como base.

    # valid_features_example esta en schemas

    # aqui predictor.predict realiza la prediccion del vino y guarda el resultado en
    # output
    output = predictor.predict(payload.features)

    # convertimos el resultado interno en un objeto Prediction.
    # Como esa clase no declara raw_score, no aparecera
    # en la respuesta publica.
    prediction = Prediction.model_validate(output, from_attributes=True)

    # TODO S9.1e: este dict expone `raw_score` y la confianza sin redondear.
    # Declara `-> PredictionResponse` y construye el modelo; para pasar de la
    # dataclass ModelOutput a Prediction investiga `from_attributes=True`.

    # asdict(output) convierte ese resultado en un diccionario que incluye raw_score
    # y confidence sin redondear.
    # return {"prediction": asdict(output), "request_id": request_id}

    # devolvemos la respuesta completa
    return PredictionResponse(
        prediction=prediction,
        request_id=request_id,
        served_at=datetime.now(UTC),
    )

    # el porblema es precisamente lo aprendido en M1, estamos devolviendo informacion
    # interna del modelo.
