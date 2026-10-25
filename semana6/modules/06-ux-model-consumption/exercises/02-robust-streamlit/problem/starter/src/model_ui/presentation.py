"""TODOs de la vista UX: copy de salida y traducción de errores."""

from __future__ import annotations

from pydantic import ValidationError

from model_ui.contracts import PredictionPayload, PredictionView, UserFacingError
from model_ui.errors import (
    ArtifactUnavailableError,
    BackendInferenceError,
    InferenceTimeoutError,
    InputContractError,
)
from model_ui.policies import (
    DEFAULT_CONFIDENCE_POLICY,
    DEFAULT_LATENCY_POLICY,
    ConfidencePolicy,
    LatencyPolicy,
    classify_confidence,
    classify_latency,
)

QUALITY_LABELS = {
    "needs_review": "Requiere revisión",
    "acceptable": "Resultado aceptable",
    "excellent": "Resultado excelente",
}

CONFIDENCE_COPY = {
    "low": (
        "Confianza baja",
        "El resultado es orientativo y requiere revisión; "
        "la confianza no es una garantía.",
    ),
    "medium": (
        "Confianza intermedia",
        "Usa el resultado como señal orientativa y revisa su contexto antes de actuar.",
    ),
    "high": (
        "Confianza alta",
        "La confianza es alta para este modelo, pero no garantiza "
        "que la decisión sea correcta.",
    ),
}

LATENCY_COPY = {
    "within_target": (
        "Dentro del objetivo",
        "La respuesta quedó dentro del objetivo de la demo.",
    ),
    "above_target": (
        "Por encima del objetivo",
        "La respuesta llegó, pero la latencia supera el objetivo técnico de la demo.",
    ),
}
# policies.py decide que clasificacion corresponde a cada numero
# y presentation.py utiliza esas clasificaciones para preparar
# los textos y lso datos que vera el usuario

# esta funcion no hace una prediccion. El modelo ya la ha hecho.
# Nosostros solo estamos preparando la informacion para mostrarla en streamlit.


def build_prediction_view(
    prediction: PredictionPayload,  # objeto que contienene los resutlados del modelo
    latency_ms: float,  # un numero que inidica cuanto ha tardado el modelo en responder
    *,
    confidence_policy: ConfidencePolicy = DEFAULT_CONFIDENCE_POLICY,
    latency_policy: LatencyPolicy = DEFAULT_LATENCY_POLICY,
) -> PredictionView:
    """TODO: construye la vista con etiquetas, confianza, latencia y versiones."""

    # clasificamos la cofianza y la latencia en las categorias que
    # ya definimos en policy.py por ejemplo la funcion recive 0.74 y devuelve "medium"
    confidence_level = classify_confidence(prediction.confidence, confidence_policy)
    latency_status = classify_latency(latency_ms, latency_policy)

    # buacamos los mensajes correspondientes
    confidence_label = CONFIDENCE_COPY[confidence_level][0]
    confidence_message = CONFIDENCE_COPY[confidence_level][1]

    latency_label = LATENCY_COPY[latency_status][0]
    latency_message = LATENCY_COPY[latency_status][1]

    # todo esto se saca de la clase predictionView de contracts
    return PredictionView(  # toda la info que queremos mostrar en streamlit
        quality_band=prediction.quality_band,  # acceptable"
        quality_label=QUALITY_LABELS[prediction.quality_band],  # resultado acceptable"
        confidence=prediction.confidence,  # 0.74
        confidence_level=confidence_level,  # medium
        confidence_label=confidence_label,  # confianza intermedia
        confidence_message=confidence_message,  # mensaje
        latency_ms=round(latency_ms, 3),  # redondeamos a 3 decimales
        latency_status=latency_status,
        latency_label=latency_label,
        latency_message=latency_message,
        model_version=prediction.model_version,
        preprocessing_version=prediction.preprocessing_version,
    )


def to_user_facing_error(error: Exception, request_id: str) -> UserFacingError:
    """TODO: asigna código estable, mensaje accionable y recuperación."""
    # los datos introducidos no son validos
    if isinstance(error, (InputContractError, ValidationError)):
        return UserFacingError(
            code="invalid_input",
            title="Revisa los datos",
            message="algun de los datos introducidos no es valido",
            recovery="comprueba los valores y vuelve a intentarlo",
            request_id=request_id,
        )

    # no se puede cargar el modelo
    if isinstance(error, ArtifactUnavailableError):
        return UserFacingError(
            code="artifact_unavailable",
            title="Modelo no disponible",
            message="No se ha podido cargar el modelo",
            recovery="Comprueba que el modelo est configurado correctamente",
            request_id=request_id,
        )

    # la prediccion tarda demasiado
    if isinstance(error, InferenceTimeoutError):
        return UserFacingError(
            code="timeout",
            title="La prediccion esta tardando demasiado",
            message="no se ha obtenido una respuesta a tiempo",
            recovery="espera unos segundos y vuelve a intentarlo",
            request_id=request_id,
        )

    # el modelo falla al realizar la prediccion
    if isinstance(error, BackendInferenceError):
        return UserFacingError(
            code="predicition_error",
            title="error en la prediccion",
            message="No se ha podido obtener una prediccion valida",
            recovery="vuelve a intentarlo o avisa al responsable",
            request_id=request_id,
        )

    # ocurre cualquier otro error no previsto
    return UserFacingError(
        code="prediction_error",
        title="no se pudo completar la prediccion",
        message="ha ocurrido un problema al procesar la peticion",
        recovery=(
            "Vuelve a intentarlo y, si el problema continúa, "
            "comunica el identificador de la petición."
        ),
        request_id=request_id,
    )
