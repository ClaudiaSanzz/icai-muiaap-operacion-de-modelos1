"""Cliente HTTP que adapta la API Wine al contrato de inferencia de la UI."""

from __future__ import annotations

from collections.abc import Mapping
from threading import local
from typing import Any

import requests
from pydantic import ValidationError  # noqa: F401 - pista para el TODO S7.4

from model_ui.contracts import PredictionPayload
from model_ui.errors import (  # noqa: F401 - pistas para el TODO S7.2
    ArtifactUnavailableError,
    BackendInferenceError,
    InferenceTimeoutError,
    InputContractError,
)


class HttpInferenceGateway:
    """Implementa la frontera de inferencia mediante una llamada HTTP REST."""

    def __init__(
        self,
        base_url: str,
        *,
        timeout: float = 5.0,
        session: Any | None = None,
    ) -> None:
        normalized = base_url.strip().rstrip("/")
        if not normalized:
            raise ValueError("base_url no puede estar vacia")
        if timeout <= 0:
            raise ValueError("timeout debe ser positivo")

        self._prediction_url = f"{normalized}/v1/predictions"  # guarda las URL completa
        self._timeout = float(timeout)  # guarda el tiempo maximo de espera configurado
        self._session = session if session is not None else requests.Session()
        self._request_context = local()
        self.last_request_id: str | None = None

    @property
    def last_request_id(self) -> str | None:
        """Devuelve el identificador de la ultima llamada en el contexto actual."""

        return getattr(self._request_context, "request_id", None)

    @last_request_id.setter
    def last_request_id(self, value: str | None) -> None:
        self._request_context.request_id = value

    def predict(self, values: Mapping[str, object]) -> PredictionPayload:
        """Envia la muestra por HTTP y devuelve el contrato interno de S6."""

        # TODO S7.1: envia POST a self._prediction_url con json={"features": ...},
        # Accept application/json y self._timeout. Compruebalo con el test de llamada.
        # TODO S7.2: traduce Timeout, ConnectionError y RequestException a los
        # errores de dominio que ya entiende PredictionController.
        # TODO S7.3: lee un objeto JSON, conserva request_id y diferencia 422/503
        # del resto de errores HTTP.
        # TODO S7.4: valida body["prediction"] como PredictionPayload; un dict sin
        # validar no satisface el contrato de salida.

        # Borramos el ID de la petición anterior.
        self.last_request_id = None
        try:
            response = self._session.post(
                self._prediction_url,
                json={"features": dict(values)},
                headers={"Accept": "application/json"},
                timeout=self._timeout,
            )
        except requests.Timeout as exc:
            raise InferenceTimeoutError(
                "La inferencia superó el tiempo permitido por el consumidor"
            ) from exc
        except requests.ConnectionError as exc:
            raise ArtifactUnavailableError(
                "El bundle o el backend necesario no está disponible."
            ) from exc
        except requests.RequestException as exc:
            raise BackendInferenceError(
                "El backend no pudo producir una salida compatible."
            ) from exc

        # Guardamos el ID incluso si la respuesta es un error.
        self.last_request_id = self._header_request_id(response)

        # Si falla la petición HTTP, convertimos el error de requests
        # en un error que nuestro controlador ya sabe gestionar.
        # Timeout = tarda demasiado; ConnectionError = no conecta.

        if response.status_code == 422:
            raise InputContractError(
                "La petición no cumple el contrato de entrada del modelo."
            )
        if response.status_code == 503:
            raise ArtifactUnavailableError(
                "El bundle o el backend necesario no está disponible."
            )
        if not 200 <= response.status_code < 300:
            raise BackendInferenceError(f"Error HTTP {response.status_code}")

        # Comprobamos el status HTTP antes de leer el JSON.
        # 422 = datos incorrectos; 503 = servicio no disponible.
        # solo aceptamos respuestas 2xx.

        body = self._read_object(response)
        self.last_request_id = self._request_id(response, body)

        try:
            prediction = PredictionPayload.model_validate(body["prediction"])
        except (KeyError, ValidationError, TypeError) as exc:
            raise BackendInferenceError("Predicción recibida no válida") from exc

        return prediction

        # Comprobamos que la predicción recibida cumple el contrato de S6.
        # Si es incorrecta, lanzamos un error; si es válida, la devolvemos.

    # statismethod es una funcion de una clase que trabaja por su cuenta, al usarla
    # no necesita self porque solo usa los datos que le pasamos.
    # self es para cuando una funcion necesita informacion guardada en el objeto

    @staticmethod
    def _read_object(response: Any) -> dict[str, Any]:
        """Lee una respuesta JSON que debe representar un objeto."""

        # TODO S7.3: usa response.json(), traduce ValueError y rechaza listas u
        # otros valores que no sean un objeto JSON.
        try:
            body = response.json()
        except ValueError as exc:
            raise BackendInferenceError("JSON de respuesta invalido") from exc

        if not isinstance(body, dict):
            raise BackendInferenceError("la respuesta debe ser un objeto JSON")

        return body

    @staticmethod
    def _request_id(response: Any, body: dict[str, Any]) -> str | None:
        """Obtiene request_id del cuerpo y usa la cabecera como alternativa."""

        # TODO S7.3: prioriza body["request_id"] y usa X-Request-Id como fallback.
        request_id = body.get("request_id")

        if isinstance(request_id, str):
            return request_id

        return HttpInferenceGateway._header_request_id(response)

    # Buscamos el request_id en el JSON.
    # Si no aparece, lo buscamos en la cabecera HTTP.

    @staticmethod
    def _header_request_id(response: Any) -> str | None:
        headers = getattr(response, "headers", {})
        return headers.get("X-Request-Id")
