from fastapi import APIRouter

from wine_api.dependencies import PredictorDep, RequestIdDep
from wine_api.errors import ModelUnavailableError
from wine_api.schemas import ErrorResponse, HealthResponse  # noqa: F401 - pista para S9.1d

SERVICE_NAME = "wine-quality-prediction"

# TODO S9.3a: declara `tags=["health"]` en el router, no en include_router().
router = APIRouter(tags=["health"])


# TODO S9.3b: añade `summary=`, `response_description=` y un docstring que diga
# cuándo usar el endpoint y qué significa un 503. Documenta el 503 con
# `responses={503: {"model": ErrorResponse, "description": ...}}`.
@router.get(
    "/health",
    summary="Check service health",  # titulo que aparece en swagger
    response_description="Service and model status",  # respuesta correcta (200)
    responses={
        503: {  # indica que tambien puede devolver un 503
            "model": ErrorResponse,  # modelo pydantic que define la estructura del eror
            "description": "Prediction model is unavailable",
        }
    },
)
def read_health(predictor: PredictorDep, request_id: RequestIdDep) -> HealthResponse:
    """Comprueba si el servicio está funcionando y el modelo está disponible.

    Este endpoint se utiliza para consultar el estado de la API.
    Si el modelo no está cargado, devuelve un error HTTP 503.
    """

    # TODO S9.2f: sustituye el HTTPException por `ModelUnavailableError`: el
    # dominio no debería saber de HTTP y el manejador produce el sobre común.
    if not predictor.is_ready():
        raise ModelUnavailableError()
    # TODO S9.1d: declara `-> HealthResponse` y devuelve una instancia.

    # hay que ir a schemas a HealthResponse(BaseModel) para ver que campos espera
    # ese modelo.

    # lo que nos piden aqui es que en lugar de devolver un dict,
    # devuelvas un objeto de Pydantic de tipo HealthResponse.
    return HealthResponse(  # es un modelo de Pydantic que cmrpueba que los datos tienen
        # la estructura y los tipos correctos
        # hay que cambiar los {} por () y los : por =
        status="ok",
        service=SERVICE_NAME,
        model_status="ready",
        model_version=predictor.model_version,
        request_id=request_id,
    )
