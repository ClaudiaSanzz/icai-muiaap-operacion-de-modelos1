"""TODOs del controlador de estados independiente de Streamlit."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from time import perf_counter
from uuid import uuid4

from model_ui.contracts import PredictionPayload, UiState
from model_ui.gateway import InferenceGateway
from model_ui.presentation import build_prediction_view, to_user_facing_error
from model_ui.telemetry import Telemetry

StateEmitter = Callable[[UiState], None]
Clock = Callable[[], float]
RequestIdFactory = Callable[[], str]


class PredictionController:
    """Orquesta loading, gateway, errores y telemetría."""

    def __init__(
        self,
        gateway: InferenceGateway,
        *,
        telemetry: Telemetry | None = None,
        clock: Clock = perf_counter,
        request_id_factory: RequestIdFactory | None = None,
    ) -> None:
        self.gateway = gateway
        self.telemetry = telemetry or Telemetry()
        self._clock = clock
        self._request_id_factory = request_id_factory or (lambda: uuid4().hex[:10])

    # esta funcion se encarga de organzar todo lo que ocurre cuando pedimos
    # una prediccion
    # antes pulsabamso ejecutar inferencia y aparecia el resultado
    # ahora queremos controlar tambien que ocurre antes, durante
    # y despues de esa prediccion
    def submit(
        self,
        values: Mapping[str, object],  # datos del formulario
        *,
        emit: StateEmitter | None = None,  # avisa de que el estado ha cambiado
    ) -> UiState:
        """TODO: emite loading, mide, valida la salida y devuelve success/error."""

        # creamos un identificador para esta peticion
        request_id = self._request_id_factory()  # esta funcion esta en init

        # indicamos que empieza la prediccion
        loading = UiState(phase="loading", request_id=request_id)
        if emit is not None:
            emit(loading)

        # guardamos el momento en el que empieza
        inicio = self._clock()
        try:
            # ejecutamos el modelo
            resultado = self.gateway.predict(values)
            prediction = PredictionPayload.model_validate(resultado)
            latency_ms = max(
                0.0, (self._clock() - inicio) * 1000
            )  # cuanto a tardado en ms
            view = build_prediction_view(prediction, latency_ms)
            # registramos la prediccion
            self.telemetry.record_success(
                latency_ms,
                model_version=prediction.model_version,
                preprocessing_version=prediction.preprocessing_version,
            )

            # cambiamos el estado a success
            state = UiState(
                phase="success",
                request_id=request_id,
                view=view,
            )

        except Exception as error:
            # calculamos cuanto tiempo ha pasado hasta el error
            latency_ms = max(0.0, (self._clock() - inicio) * 1000)

            # convertimos el error tecnico en un mensaje comprensible
            user_error = to_user_facing_error(error, request_id)

            self.telemetry.record_error(user_error.code, latency_ms)

            # cambiamos el estado a error
            state = UiState(
                phase="error",
                request_id=request_id,
                error=user_error,
            )

        if emit is not None:
            emit(state)

        return state
