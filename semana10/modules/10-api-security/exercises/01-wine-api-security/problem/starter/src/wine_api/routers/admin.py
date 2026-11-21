from fastapi import APIRouter, Depends  # noqa: F401 - pista para S10.3d

from wine_api.dependencies import RequestIdDep, SettingsDep  # noqa: F401
from wine_api.rate_limit import RateLimiterDep  # noqa: F401 - pista para S10.3d
from wine_api.schemas import ClientUsage, ErrorResponse, UsageResponse  # noqa: F401
from wine_api.security import require_scope

# TODO S10.3d: protege este router con el scope `admin` (a nivel de
# `APIRouter`, como en predicciones) y crea `GET /v1/admin/usage`:
# - devuelve `UsageResponse` (tipo de retorno, no `dict`) con un `ClientUsage`
#   por cliente configurado, ordenados por nombre: nombre, peticiones en la
#   ventana actual (`limiter.usage(...)`) y límite por minuto;
# - nunca incluyas la clave: ¿qué campo de `ClientConfig` NO debe salir?
# - añade `summary`, `response_description` y un docstring para /docs (los
#   tests de S9.3 lo exigen a toda operación).
# Comprobación: uv run pytest -q tests/test_s10_3_authorization.py
# TODO S10.6a: documenta también aquí los 401 y 403 con `ErrorResponse`.
router = APIRouter(
    prefix="/v1/admin",
    tags=["admin"],
    dependencies=[Depends(require_scope("admin"))],
    responses={
        401: {
            "model": ErrorResponse,
            "description": "Api key invalida o ausente",
        },
        403: {
            "model": ErrorResponse,
            "description": "Permisos insuficientes",
        },
    },
)


@router.get(
    "/usage",
    summary="Consultar el uso de la API ",
    response_description="Peticiones realizadas por cada cliente",
)
def get_usage(
    settings: SettingsDep,
    limiter: RateLimiterDep,
    request_id: RequestIdDep,
) -> UsageResponse:
    """Consulta el número de peticiones realizadas por cada cliente.

    Devuelve las peticiones utilizadas durante la ventana actual y
    el límite permitido. No muestra las claves de autenticación.
    """

    clientes = []

    # recorremos los clientes ordenados por nombre
    for nombre, config in sorted(settings.clients.items()):
        clientes.append(
            ClientUsage(
                client=nombre,
                requests_in_window=limiter.usage(nombre),
                limit=config.rate_limit_per_minute,
            )
        )
    return UsageResponse(clients=clientes, request_id=request_id)


# Qué campo de ClientConfig nunca debe aparecer en la respuesta?
# key, porque contiene la API key secreta
