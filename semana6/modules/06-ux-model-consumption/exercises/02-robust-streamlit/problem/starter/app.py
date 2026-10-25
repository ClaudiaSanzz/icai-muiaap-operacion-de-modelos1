"""Starter S6: snapshot de la app de S5 con cableado avanzado pendiente."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from model_ui.contracts import UiState
from model_ui.controller import PredictionController
from model_ui.gateway import (
    FEATURE_NAMES,
    DemoGateway,
    InferenceGateway,
    PackagedBundleGateway,
    UnavailableGateway,
)
from model_ui.session import (
    LAST_STATE_KEY,
    LAST_VALUES_KEY,
    TELEMETRY_KEY,
    clear_last_state,
    initialize_session_state,
)

FEATURE_FIELDS = (
    ("fixed_acidity", "Fixed acidity", 0.0, 20.0, 7.4),
    ("volatile_acidity", "Volatile acidity", 0.0, 2.0, 0.7),
    ("citric_acid", "Citric acid", 0.0, 2.0, 0.0),
    ("residual_sugar", "Residual sugar", 0.0, 20.0, 1.9),
    ("chlorides", "Chlorides", 0.0, 1.0, 0.076),
    ("free_sulfur_dioxide", "Free sulfur dioxide", 0.0, 100.0, 11.0),
    ("total_sulfur_dioxide", "Total sulfur dioxide", 0.0, 300.0, 34.0),
    ("density", "Density", 0.98, 1.01, 0.9978),
    ("ph", "pH", 2.5, 4.5, 3.51),
    ("sulphates", "Sulphates", 0.0, 3.0, 0.56),
    ("alcohol", "Alcohol", 5.0, 20.0, 9.4),
)

assert tuple(field[0] for field in FEATURE_FIELDS) == FEATURE_NAMES


def build_gateway(bundle_value: str | None) -> InferenceGateway:
    """Selecciona el bundle configurado o conserva el gateway demo de S5."""

    if not bundle_value:
        return DemoGateway()
    try:
        return PackagedBundleGateway.from_bundle_path(Path(bundle_value))
    except Exception as error:  # noqa: BLE001 - se convierte en estado visible
        return UnavailableGateway(str(error))


def collect_values(st: Any) -> tuple[bool, dict[str, float]]:
    """Formulario heredado de S5; no es un TODO de esta semana."""

    values: dict[str, float] = {}
    with st.form("wine_quality_form"):
        st.caption("Formulario de S5: la inferencia se envía al pulsar el botón.")
        columns = st.columns(2)
        for index, (name, label, minimum, maximum, default) in enumerate(
            FEATURE_FIELDS
        ):
            with columns[index % 2]:
                values[name] = st.number_input(
                    label,
                    min_value=minimum,
                    max_value=maximum,
                    value=default,
                    key=f"input_{name}",
                )
        submitted = st.form_submit_button("Ejecutar inferencia")
    return submitted, values


def get_cached_gateway(st: Any, bundle_value: str | None) -> InferenceGateway:
    """TODO: usa `st.cache_resource` sobre el gateway, no sobre la respuesta."""

    # queremos que el gateway se cree un avez y se reutilice mientras siga en cache
    @st.cache_resource
    def cargar_gateway(ruta_bundle: str | None) -> InferenceGateway:
        return build_gateway(ruta_bundle)

    return cargar_gateway(bundle_value)


def render_state(st: Any, state: UiState, target: Any | None = None) -> None:
    """TODO: presenta idle/loading/success/error en un target de Streamlit."""
    # Si nos pasan una zona de pantalla, la utilizamos.
    # Si no, mostramos los resultados directamente en Streamlit.
    pantalla = target if target is not None else st

    # todavía no hemos hecho ninguna predicción
    if state.phase == "idle":
        pantalla.info("Introduce los datos del vino y pulsa Ejecutar inferencia.")
        return

    # Estamos realizando la predicción
    if state.phase == "loading":
        pantalla.info("Estamos procesando los datos...")
        return

    # La predicción ha terminado correctamente
    if state.phase == "success" and state.view is not None:
        # Recuperamos los resultados que preparamos en presentation.py
        view = state.view

        pantalla.success(view.quality_label)

        # Mostramos las tres métricas principales
        col1, col2, col3 = pantalla.columns(3)

        col1.metric("Categoría", view.quality_label)
        col2.metric("Confianza", f"{view.confidence:.0%}")
        col3.metric("Latencia", f"{view.latency_ms:.0f} ms")

        # Mensaje para interpretar la confianza
        if view.confidence_level == "low":
            pantalla.warning(view.confidence_message)
        else:
            pantalla.info(view.confidence_message)

        # Avisamos si la predicción ha tardado más de lo esperado
        if view.latency_status == "above_target":
            pantalla.warning(view.latency_message)
        else:
            pantalla.caption(view.latency_message)

        # Dejamos los detalles técnicos en un desplegable
        with pantalla.expander("Trazabilidad"):
            st.write(f"Modelo: {view.model_version}")
            st.write(f"Preprocesado: {view.preprocessing_version}")
            st.write(f"Request ID: {state.request_id}")

        return

        # Ha ocurrido un error
    if state.phase == "error" and state.error is not None:
        error = state.error

        pantalla.error(error.title)
        pantalla.write(error.message)
        pantalla.info(error.recovery)
        pantalla.caption(f"Request ID: {error.request_id}")


def main() -> None:
    """Ejecuta la app de S5 con estado avanzado de S6."""

    try:
        import streamlit as st
    except ModuleNotFoundError as error:
        raise SystemExit(
            "Instala Streamlit con `uv run --with streamlit streamlit run app.py`."
        ) from error

    st.set_page_config(page_title="Wine Quality · S6", page_icon="🍷")
    st.title("Inferencia de calidad de vino")
    st.caption("S6: la app de S5 ahora conserva estado y comunica la operación.")

    initialize_session_state(st.session_state)
    bundle_value = os.getenv("MODEL_UI_BUNDLE")
    gateway = get_cached_gateway(st, bundle_value)
    telemetry = st.session_state[TELEMETRY_KEY]
    controller = PredictionController(gateway, telemetry=telemetry)

    submitted, values = collect_values(st)
    state_slot = st.empty()
    if submitted:
        st.session_state[LAST_VALUES_KEY] = values
        with st.status("Ejecutando inferencia…", expanded=False) as status:
            state = controller.submit(
                values,
                emit=lambda event: render_state(st, event, state_slot),
            )
            st.session_state[LAST_STATE_KEY] = state
            status.update(
                label=(
                    "Inferencia completada"
                    if state.phase == "success"
                    else "La inferencia necesita atención"
                ),
                state="complete" if state.phase == "success" else "error",
            )

    if st.button("Limpiar último resultado"):
        clear_last_state(st.session_state)
        st.rerun()

    state = st.session_state[LAST_STATE_KEY]
    render_state(st, state)
    if state.phase == "error" and st.session_state[LAST_VALUES_KEY]:
        if st.button("Reintentar"):
            retry_state = controller.submit(st.session_state[LAST_VALUES_KEY])
            st.session_state[LAST_STATE_KEY] = retry_state
            st.rerun()

    st.divider()
    st.subheader("Telemetría de la sesión")
    st.json(telemetry.snapshot().__dict__)
    st.caption("Solo se muestran agregados; no se guardan las features en Telemetry.")


if __name__ == "__main__":
    main()
