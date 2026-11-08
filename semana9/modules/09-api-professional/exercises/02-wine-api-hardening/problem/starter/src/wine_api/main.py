"""Punto de entrada de la API: `fastapi dev` usa `wine_api.main:app`."""

import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from wine_api.errors import install_error_handlers
from wine_api.predictor import Predictor, build_predictor
from wine_api.request_id import request_id_middleware
from wine_api.routers import health, predictions

# TODO S9.3g: completa los metadatos que lee el consumidor en /docs:
# `version` (¿mayor, menor o parche tras S9.1c?), `summary`, una `description`
# en Markdown que explique `request_id` y el sobre de error, y `openapi_tags`
# con una descripción por tag. Comprobación: tests/test_s9_3_openapi.py
API_VERSION = "1.1.0"


def create_app(predictor: Predictor | None = None) -> FastAPI:
    """Crea la aplicación; los tests inyectan su propio predictor."""

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
        app.state.predictor = predictor or build_predictor(
            os.environ.get("WINE_API_MODE", "ready")
        )
        yield

    app = FastAPI(
        title="Wine Quality API",
        version=API_VERSION,
        summary="API para predecir la calidad del vino",
        description=(
            "API que predice la calidad del vino a partir de 11 caracteristicas \n\n"
            "Cada preticion tiene un 'request_id' para poder identificarla. \n\n"
            "Los errores utilizan un sobre común con `code`, `message`, "
            "`fields` y `request_id`."
        ),
        openapi_tags=[
            {
                "name": "health",
                "description": "comprueba el estado del servicio y del modelo",
            },
            {
                "name": "predictions",
                "description": "Permite realizar predicciones de calidad del vino",
            },
        ],
        lifespan=lifespan,
    )

    app.middleware("http")(request_id_middleware)
    install_error_handlers(app)
    app.include_router(health.router)
    app.include_router(predictions.router)
    return app


app = create_app()
