"""Estado de sesión de Streamlit aislado para poder probarlo sin Streamlit."""

from __future__ import annotations

from collections.abc import MutableMapping

from model_ui.contracts import UiState
from model_ui.telemetry import Telemetry

LAST_STATE_KEY = "last_state"  # guarda el estado de la ultima peticion
TELEMETRY_KEY = (
    "telemetry"  # se mantiene porque queremos conservar los datos acumualados
)
LAST_VALUES_KEY = "last_values"


def initialize_session_state(
    session_state: MutableMapping[str, object],
) -> None:
    """TODO: crea solo las entradas de sesion que todavía no existan."""
    # setdefault crea la variable solo si no existe, asi que no perdemos informacion
    # al actualizarse la app
    session_state.setdefault(LAST_STATE_KEY, UiState(phase="idle"))
    session_state.setdefault(TELEMETRY_KEY, Telemetry())
    session_state.setdefault(LAST_VALUES_KEY, {})
    # last_values se pone a none cuando limpiamos, porque ya no necesitamos los valores
    # de la ultima peticion


# en contracts esta la clase uistate que sirve para guardar el estado de una peticion
# y la app puede estar en idle(inactivo), loading, success o error
# con esto :  UiState(phase="idle")) le esto diciendo si todavia no existe un estado,
# crea uno que indique que no se ha realizado ninguna peticion

# en telemetry esta la clase telemetry que cuenta las peticiones que hemos realizado
# y registra informacion general de su funcionamiento.
# con esto: TELEMETRY_KEY, Telemetry()) le estoy diciendo si todavia no existe la
# telemetria, crea una con los contadores a cero.

# aqui (LAST_VALUES_KEY, {}) creo un diccionario vacio porque todavia no hemos enviado
# datos.


def clear_last_state(session_state: MutableMapping[str, object]) -> None:
    """TODO: vuelve a idle sin perder la telemetría acumulada."""

    session_state[LAST_STATE_KEY] = UiState(phase="idle")
    session_state[LAST_VALUES_KEY] = {}


# aqui lo que queremos es borrar la ultima prediccion, asi que reemplazamos el estado
# anterior por uno nuevo. Pero, no tocamos TELEMETRY_KEY porque aunque limpiemos
# el resultado, seguimos conservando las estadisitcas de las predicciones realizadas.
