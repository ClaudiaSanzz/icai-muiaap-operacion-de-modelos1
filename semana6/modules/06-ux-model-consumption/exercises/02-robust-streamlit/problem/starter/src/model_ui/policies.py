"""Políticas explícitas que el alumnado puede reutilizar en la UI."""

from dataclasses import dataclass

from model_ui.contracts import ConfidenceLevel, LatencyStatus


@dataclass(frozen=True)
class ConfidencePolicy:
    """Umbrales de comunicación, no de aprobación del modelo."""

    low_below: float = 0.60
    high_from: float = 0.85


@dataclass(frozen=True)
class LatencyPolicy:
    """Objetivo técnico de la demo."""

    target_ms: float = 300.0


DEFAULT_CONFIDENCE_POLICY = ConfidencePolicy()
DEFAULT_LATENCY_POLICY = LatencyPolicy()


def classify_confidence(
    confidence: float, policy: ConfidencePolicy = DEFAULT_CONFIDENCE_POLICY
) -> ConfidenceLevel:
    """TODO: valida [0, 1] y devuelve low/medium/high según policy."""

    # Comprobamos que la confianza sea válida
    if confidence < 0 or confidence > 1:
        raise ValueError("La confianza debe estar entre 0 y 1")

    # Confianza baja: menos del 60%
    if confidence < policy.low_below:
        return "low"

    # Confianza media: entre el 60% y el 85%
    if confidence < policy.high_from:
        return "medium"

    # Confianza alta: 85% o más
    return "high"


def classify_latency(
    latency_ms: float, policy: LatencyPolicy = DEFAULT_LATENCY_POLICY
) -> LatencyStatus:
    """TODO: devuelve within_target o above_target para una latencia válida."""

    if latency_ms < 0:
        raise ValueError("La latencia no puede ser negativa")
    # Si tarda 300 ms o menos
    if latency_ms <= policy.target_ms:
        return "within_target"
    else:
        return "above_target"
    # Si tarda más de 300 ms
