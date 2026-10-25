"""Starter: conecta una función de inferencia pura con Streamlit."""

from collections.abc import Callable
from typing import Any

from churn_demo.model import ChurnPrediction, predict

Predictor = Callable[..., ChurnPrediction]


def collect_profile(st: Any) -> tuple[bool, dict[str, object]]:
    """Renderiza cuatro widgets dentro de un único formulario."""
    # contrato de widgets/diccionario
    with st.form(
        "churn_form"
    ):  # st.froma es un contenedor donde metes varios widgets y churn form es el nombre
        values = {
            "tenure_months": st.slider(
                "Antigüedad", min_value=0, max_value=120, value=12, key="tenure_months"
            ),
            "monthly_spend_eur": st.number_input(
                "Gasto_mensual",
                min_value=0,
                max_value=300,
                value=60,
                key="monthly_spend_eur",
            ),
            "support_calls": st.slider(
                "Llamadas_a_soporte",
                min_value=0,
                max_value=20,
                value=1,
                key="support_calls",
            ),
            "has_annual_contract": st.checkbox(
                "Contrato_anual", value=False, key="has_annual_contract"
            ),
            # st_slider: seleccionar un numero moviendo una barra
            # st.number_input: escribir un numero en una casilla
            # st.checkbox: marcar o desmacar una casilla (true/false)
        }
        # guardo el booleano que me devuelve
        submitted = st.form_submit_button("Calcular riesgo")
    return submitted, values  # la def me dice que me tiene que devolver la funcion 2


# st:any recibe streamlit, result recibe el diccionario que devuelve predict 
# none es que no tiene que devolver nada
def render_prediction(st: Any, result: ChurnPrediction) -> None:
    """Muestra etiqueta, score orientativo y explicación."""

    # si sale will churn true es que hay baja probable y manda el warning
    # si sale will churn false es que hay permanencia
    if result["will_churn"]:
        st.warning(result["label"])
    else:
        st.success(result["label"])

    # st.metric tiene que recibir una etiqueta y un valor
    st.metric(
        "Score orientativo", f"{result['risk_score']:.2f}"
    )  # esto es que limito a 2 decimales

    st.write(result["explanation"])  # escribe la explicacion


# def run app tuene que llamar a collect:profile() 
# y recoger los valores de submitted, values
def run_app(st: Any, predictor: Predictor) -> None:
    """Conecta submit, llamada al predictor y actualización visible."""

    submitted, values = collect_profile(st)

    if not submitted:
        return

    try:
        result = predictor(**values)
        render_prediction(st, result)
    except ValueError:
        st.error("No se pudo calcular la prediccion")


def main() -> None:
    """Configura la página real y delega el flujo comprobable en run_app."""
    import streamlit as st

    st.set_page_config(page_title="Churn sintético · S5", page_icon="📉")
    st.title("¿Qué cliente podría darse de baja?")
    st.caption("Caso docente sintético; el score no es una probabilidad calibrada.")
    run_app(st, predict)


if __name__ == "__main__":
    main()


