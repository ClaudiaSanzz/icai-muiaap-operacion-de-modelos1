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


class ModelUnavailableError(WineApiError):
    status_code = 503
    code = ErrorCode.MODEL_UNAVAILABLE
    message = "The prediction model is not ready"


def error_response(
    request: Request,
    status_code: int,
    code: ErrorCode,
    message: str,
    fields: list[FieldError] | None = None,
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
        headers={REQUEST_ID_HEADER: request_id},
    )


def field_path(loc: Sequence[Any]) -> str:
    """Convierte `("body", "features", "alcohol")` en `features.alcohol`."""

    parts = [str(part) for part in loc if part != "body"]
    return ".".join(parts) or "body"


async def handle_validation_error(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    # TODO S9.2a: FastAPI responde 422 con {"detail": [...]}, que no es nuestro
    # contrato. Recorre `exc.errors()`: cada error trae `type`, `loc` y `msg`.
    # - Si algún `type` es "json_invalid", el cuerpo no es JSON: 400 con
    #   `ErrorCode.INVALID_JSON` y sin `fields`.
    # - Si no, 422 con `ErrorCode.VALIDATION_ERROR` y una lista de FieldError
    #   (usa `field_path`). Nunca copies `input`: puede contener datos del
    #   usuario. Comprobación: tests/test_s9_2_errors.py

    # el objetivo aqui es distinguir 2 situaciones:
    # 400 - INVALID JSON: el cuerpo de la peticion contiene un JSON mal escrito
    # 422 - VALIDATION ERROR: el JSON esta bien escrito, pero alguno de sus valores
    # incumple el contrato. Por ejemplo, alcohol=30 cuando el maximo permitido es 20.

    for error in exc.errors():
        if error["type"] == "json_invalid":
            return error_response(  # error response ya es una funcion implementada
                request,
                400,
                ErrorCode.INVALID_JSON,
                "Invalid JSON",
            )

    fields = []
    for error in exc.errors():
        fields.append(  # añade ese error a la lista
            FieldError(
                field=field_path(error["loc"]),  #  # obtiene el nombre del campo
                message=error["msg"],  # obtiene el mensaje explicativo
            )
        )

    return error_response(
        request,
        422,
        ErrorCode.VALIDATION_ERROR,
        "Validation error",
        fields,
    )


async def handle_api_error(request: Request, exc: WineApiError) -> JSONResponse:
    # TODO S9.2b: traduce cualquier WineApiError usando los atributos de clase
    # `status_code`, `code` y `message`. Una línea con `error_response`.

    # el profe ya ha definido la clase WineApiError y sus atributos:
    return error_response(
        request,
        exc.status_code,  # 503
        exc.code,  # model unavailable
        exc.message,  # the prediction model is not ready"
    )


async def handle_http_exception(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    # TODO S9.2c: 404 y 405 los genera Starlette, no tus rutas. Busca el código
    # en HTTP_ERROR_CODES (ErrorCode.HTTP_ERROR si no está) y responde con el
    # mismo sobre. ¿Por qué se registra la clase de Starlette y no la de FastAPI?

    # buscamos el codigo y el mensaje segun el error HTTP
    code, message = HTTP_ERROR_CODES.get(  # get busca dentro del diccionario
        exc.status_code,
        (ErrorCode.HTTP_ERROR, "HTTP error"),
    )

    # devolvemos el error con el formato comun
    return error_response(
        request,
        exc.status_code,
        code,
        message,
    )

    # ¿Por qué usamos StarletteHTTPException y no la de FastApi?
    # porque fastapi esta construido sobre Starlette, y starlette tambien genera
    # errores HTTP automaticamente, como el 404 cuando una ruta no existe. Así,
    # podemos controlar tanto los errores de Starlette como los de FastApi con el
    # mismo manejador.


async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
    # TODO S9.2d: último recurso. Registra el detalle con `logger.exception`
    # (incluye el request_id) y devuelve 500 `internal_error` con un mensaje
    # genérico. El texto de `exc` nunca sale en la respuesta.

    # queremos que si ocurre un error inesperado, la API:
    # 1. guarde el error real en los logs para poder investigarlo
    # 2. devuelva un codigo HTTP 500
    # 3, no enseñe al usuario informacion interna del servidor

    logger.exception(  # registra el error y su traceback para poder investigarlo
        "Error inesperado, request_id=%s",
        current_request_id(request),  # indica la peticion que ha fallado
        exc_info=exc,
    )

    return error_response(
        request,
        500,  # error interno del servidor
        ErrorCode.INTERNAL_ERROR,  # codigo de error de nuestro contrato
        "Unexpected server error",  # evita mostrar detalles internos al usuario
    )


def install_error_handlers(app: FastAPI) -> None:
    # TODO S9.2e: registra los cuatro manejadores con `app.add_exception_handler`
    # cuando estén implementados. Hasta entonces la API usa los errores por
    # defecto de FastAPI ({"detail": ...}), que es justo lo que queremos cambiar.

    # hasta ahora hemos creado cuatro funciones para gestionar los errores, pero
    # FastApi todavia no sabe que tiene que utilizarlas. Por eso necesitamos
    # registrarlas con app.add_exception_handler().

    # por ejemplo: cuando ocurra un WineApiError utiliza la funcion handle_api_error
    # para constuir la respuesta
    app.add_exception_handler(RequestValidationError, handle_validation_error)
    app.add_exception_handler(WineApiError, handle_api_error)
    app.add_exception_handler(StarletteHTTPException, handle_http_exception)
    app.add_exception_handler(Exception, handle_unexpected_error)
