"""Errores de dominio y su traducción a un único sobre HTTP."""

import logging
from collections.abc import Sequence
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from wine_api.request_id import REQUEST_ID_HEADER, current_request_id
from wine_api.schemas import ErrorCode, ErrorDetail, ErrorResponse, FieldError

logger = logging.getLogger("wine_api")

HTTP_ERROR_CODES = {
    404: (ErrorCode.NOT_FOUND, "The requested resource does not exist"),
    405: (ErrorCode.METHOD_NOT_ALLOWED, "Method not allowed for this resource"),
}


class WineApiError(Exception):
    """Base de los errores que la API sabe explicar al consumidor."""

    status_code = 500
    code = ErrorCode.INTERNAL_ERROR
    message = "Unexpected server error"

    # TODO S10.2b: algunos errores necesitan cabeceras propias: el 401 lleva
    # `WWW-Authenticate: ApiKey` y el 429 lleva `Retry-After`, cuyo valor
    # depende de cada caso. Añade un `__init__` que acepte `headers` por
    # instancia (y, si quieres, unas cabeceras por defecto de clase) y guárdalas
    # en `self.headers`. Después haz que `handle_api_error` las pase a
    # `error_response` y que esta las copie SIN perder `X-Request-Id`.
    # `ModelUnavailableError()` debe seguir funcionando sin argumentos.
    # Comprobación: tests/test_s10_2_authentication.py (WWW-Authenticate).

    #init se ejecuta al crear un error
    #headers permite pasar cabeceras HTTP
    #headers or {}: si no pasamos ningunam guardamos un diccionario vacio
    def __init__(self, headers: dict[str, str] | None = None): 
        self.headers = headers or {}

class ModelUnavailableError(WineApiError):
    status_code = 503
    code = ErrorCode.MODEL_UNAVAILABLE
    message = "The prediction model is not ready"


# TODO S10.2c: crea `AuthenticationError` (401, `ErrorCode.UNAUTHORIZED`,
# cabecera `WWW-Authenticate: ApiKey`). Usa el mismo mensaje cuando falta la
# clave y cuando es incorrecta: ¿qué ganaría un atacante si fueran distintos?
#
# TODO S10.3a: crea `PermissionDeniedError` (403, `ErrorCode.FORBIDDEN`).
#
# TODO S10.4a: crea `RateLimitExceededError` (429, `ErrorCode.RATE_LIMITED`).
# Recibe los segundos de espera y produce `Retry-After` (entero, en segundos)
# y, si quieres, `X-RateLimit-Limit` y `X-RateLimit-Remaining: 0`.


#con wineapierror heredamos el comportamiento del error que acabamos de modificar
class AuthenticationError(WineApiError):
    status_code = 401 #indica que no hemos podido autenticar el cliente
    code = ErrorCode.UNAUTHORIZED #idetifica el error como unaythorized
    message = "Invalid or missing API key" #utilizamos el mismo mensaje si falta la
    #clave o es incorrecta

    #tenemos que crear un error que aparezca cuando alguien intenta acceder 
    #a nuestra API sin una clave valida. este error debe devolver un 401
    def __init__(self):
        #llama al constructor de wineapierror y le pasa la cabecera HTTP
        super().__init__(headers={"WWW-Authenticate": "ApiKey"})

#esta clase represetna el error que devolveremos cuando un cliente no tenga los
#permisos necesarios
class PermissionDeniedError(WineApiError):
    status_code=403
    code = ErrorCode.FORBIDDEN
    message = "Permission denied"

#Por que usamos el mismo mensaje?
#porque si distinguimos entre una clave ausente y una incorrecta, podriamos dar
#informacion innecesaria a un atacante sobre como funciona la autenticacion

#con wineapierror heredamos el comportamiento del error que acabamos de modificar
class AuthenticationError(WineApiError):
    status_code = 401 #indica que no hemos podido autenticar el cliente
    code = ErrorCode.UNAUTHORIZED #idetifica el error como unaythorized
    message = "Invalid or missing API key" #utilizamos el mismo mensaje si falta la
    #clave o es incorrecta

    #tenemos que crear un error que aparezca cuando alguien intenta acceder 
    #a nuestra API sin una clave valida. este error debe devolver un 401
    def __init__(self):
        #llama al constructor de wineapierror y le pasa la cabecera HTTP
        super().__init__(headers={"WWW-Authenticate": "ApiKey"})

#esta clase represetna el error que devolveremos cuando un cliente no tenga los
#permisos necesarios
class PermissionDeniedError(WineApiError):
    status_code=403
    code = ErrorCode.FORBIDDEN
    message = "Permission denied"

#Por que usamos el mismo mensaje?
#porque si distinguimos entre una clave ausente y una incorrecta, podriamos dar
#informacion innecesaria a un atacante sobre como funciona la autenticacion

# TODO S10.3a: crea `PermissionDeniedError` (403, `ErrorCode.FORBIDDEN`).
#
# TODO S10.4a: crea `RateLimitExceededError` (429, `ErrorCode.RATE_LIMITED`).
# Recibe los segundos de espera y produce `Retry-After` (entero, en segundos)
# y, si quieres, `X-RateLimit-Limit` y `X-RateLimit-Remaining: 0`.

class RateLimitExceededError(WineApiError):
    status_code=429
    code=ErrorCode.RATE_LIMITED
    message="Rate limit exceeded"

    def __init__(self,retry_after:int):
        #indicamos cuantos segundos debe esperar el siguiente cliente
        super().__init__(
            headers={"retry-after": str(retry_after)}
        )

def error_response(
    request: Request,
    status_code: int,
    code: ErrorCode,
    message: str,
    fields: list[FieldError] | None = None,
    #esto permite que la funcion reciba cabeceras adicionales
    headers: dict[str, str] | None = None, 

) -> JSONResponse:
    """Construye el sobre de error; `fields` desaparece si no aplica."""

    request_id = current_request_id(request)
    body = ErrorResponse(
        error=ErrorDetail(code=code, message=message, fields=fields),
        request_id=request_id,
    )
    return JSONResponse(
        status_code=status_code,
        content=body.model_dump(mode="json", exclude_none=True),
        # el ** introduce las cabeceras adicionales dentro del diccionario y
        # conserva tambien el identificador de la peticion
        headers={**(headers or {}), REQUEST_ID_HEADER: request_id},

    )


def field_path(loc: Sequence[Any]) -> str:
    """Convierte `("body", "features", "alcohol")` en `features.alcohol`."""

    parts = [str(part) for part in loc if part != "body"]
    return ".".join(parts) or "body"


async def handle_validation_error(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    errors = exc.errors()
    if any(error["type"] == "json_invalid" for error in errors):
        return error_response(
            request, 400, ErrorCode.INVALID_JSON, "Request body is not valid JSON"
        )
    fields = [
        FieldError(field=field_path(error["loc"]), message=error["msg"])
        for error in errors
    ]
    return error_response(
        request,
        422,
        ErrorCode.VALIDATION_ERROR,
        "JSON is valid but violates the input contract",
        fields,
    )


async def handle_api_error(request: Request, exc: WineApiError) -> JSONResponse:
    return error_response(request, exc.status_code, exc.code, exc.message, headers=exc.headers)


async def handle_http_exception(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    code, message = HTTP_ERROR_CODES.get(
        exc.status_code, (ErrorCode.HTTP_ERROR, "HTTP error")
    )
    return error_response(request, exc.status_code, code, message)


async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
    # El detalle se queda en el log del servidor, nunca en la respuesta.
    logger.exception(
        "Unhandled error", extra={"request_id": current_request_id(request)}
    )
    return error_response(
        request, 500, ErrorCode.INTERNAL_ERROR, "Unexpected server error"
    )


def install_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(RequestValidationError, handle_validation_error)
    app.add_exception_handler(WineApiError, handle_api_error)
    app.add_exception_handler(StarletteHTTPException, handle_http_exception)
    app.add_exception_handler(Exception, handle_unexpected_error)
