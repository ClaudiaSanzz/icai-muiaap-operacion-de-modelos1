"""S9.4 — Tests que escribe el alumnado.

Cada test empieza en rojo con `pytest.fail`. Sustituye esa línea por el test
real; la entrega se considera completa cuando toda la suite está en verde.
"""

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from wine_api.dependencies import get_predictor  # noqa: F401 - pista S9.4a
from wine_api.export_openapi import render_openapi
from wine_api.predictor import UnavailablePredictor  # noqa: F401 - pista S9.4a


def test_prediction_returns_503_when_model_is_unavailable(
    client: TestClient, valid_payload: dict
) -> None:
    # TODO S9.4a: sin tocar el código de la API, haz que `get_predictor`
    # devuelva un UnavailablePredictor con `app.dependency_overrides` (llega
    # desde `client.app`). Comprueba status 503 y `error.code`. Limpia el
    # override al terminar para no contaminar otros tests.

    # sustituimos el predictor por uno disponible
    client.app.dependency_overrides[get_predictor] = lambda: UnavailablePredictor()

    try:
        # hacemos una peticion
        response = client.post("/v1/predictions", json=valid_payload)

        # comprobamos que devuelve el error correcto
        assert response.status_code == 503
        assert response.json()["error"]["code"] == "model_unavailable"

    finally:
        # quitamos el cambio para no afectar a otros tests
        client.app.dependency_overrides.pop(get_predictor, None)


# TODO S9.4b: convierte este test en `@pytest.mark.parametrize` con al
# menos cinco casos (justo por debajo y por encima de un rango, None, un
# texto...). Para cada uno comprueba 422 y que `fields` señala exactamente
# `features.<campo>`.
@pytest.mark.parametrize(
    "campo, valor",
    [
        ("alcohol", 4),  # Por debajo del mínimo (5)
        ("alcohol", 21),  # Por encima del máximo (20)
        ("alcohol", None),  # Valor nulo
        ("alcohol", "hola"),  # Texto en lugar de número
        ("ph", 5),  # Por encima del máximo (4.5)
    ],
)
def test_out_of_contract_values_are_rejected(
    client: TestClient, valid_payload: dict, campo, valor
) -> None:

    # Cambiamos un campo del ejemplo válido por un valor incorrecto
    valid_payload["features"][campo] = valor

    # Enviamos la petición
    response = client.post("/v1/predictions", json=valid_payload)

    # Comprobamos el error 422
    assert response.status_code == 422

    # Comprobamos que señala el campo incorrecto
    assert response.json()["error"]["fields"][0]["field"] == f"features.{campo}"


def test_range_limits_are_inclusive(client: TestClient, valid_payload: dict) -> None:
    # TODO S9.4c: los límites del contrato son inclusivos. Demuéstralo con los
    # dos extremos de `alcohol` (5 y 20): ambos deben devolver 200.

    # Probamos los dos límites permitidos de alcohol
    for alcohol in [5, 20]:
        # Cambiamos el valor de alcohol
        valid_payload["features"]["alcohol"] = alcohol

        # Hacemos la petición
        response = client.post("/v1/predictions", json=valid_payload)

        # Comprobamos que acepta el valor
        assert response.status_code == 200


def test_openapi_matches_versioned_contract() -> None:
    # TODO S9.4d: genera `contracts/openapi.json` con
    # `uv run python -m wine_api.export_openapi` y versiónalo en Git. Después
    # compara el JSON de `render_openapi()` con el archivo: si alguien cambia el
    # contrato sin querer, este test lo detecta en la revisión.

    # Ruta del contrato OpenAPI guardado
    ruta = Path(__file__).resolve().parents[1] / "contracts" / "openapi.json"

    # Leemos el JSON guardado
    with open(ruta, encoding="utf-8") as archivo:
        contrato_guardado = json.load(archivo)

    # Generamos el contrato actual y lo convertimos en diccionario
    contrato_actual = json.loads(render_openapi())

    # Comprobamos que ambos son iguales
    assert contrato_actual == contrato_guardado
