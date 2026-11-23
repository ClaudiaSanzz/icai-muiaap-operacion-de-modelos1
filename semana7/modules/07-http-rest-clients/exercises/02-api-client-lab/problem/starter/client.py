"""Starter del cliente HTTP. Completa los TODO sin modificar la API."""

from __future__ import annotations

from typing import Any

# El TODO de la práctica usará este cliente para realizar la petición HTTP.
import requests  # noqa: F401


class PredictionClientError(RuntimeError):
    def __init__(self, message: str, *, status_code: int | None = None):
        self.status_code = status_code
        super().__init__(message)


def request_prediction(
    payload: dict[str, Any],
    *,
    base_url: str = "http://127.0.0.1:8000",
    timeout: float = 5.0,
    session: Any | None = None,
) -> dict[str, Any]:
    """Envía una predicción y devuelve un objeto JSON de respuesta."""
    # TODO 3: selecciona `session` o `requests` y envía POST con `json=`,
    # `Accept` y `timeout`. Comprueba los argumentos con test_client.py.
    # TODO 4: llama a `raise_for_status()` y conserva el status de HTTPError.
    # TODO 5: traduce Timeout y ConnectionError a PredictionClientError.
    # TODO 6: convierte la respuesta con `.json()` y exige un diccionario.
    
    #usamos session si nos la pasan (para simular peticiones en los tests).
    #si no, usamos requests para hacer peticiones HTTP reales a la API
    #asi podemos probar el cliente sin depender de que el servidor esté 
    #funcionando
    if session is not None: 
        client = session
    else:
        client = requests
    try: 
        response = client.post(
            f"{base_url.rstrip('/')}/v1/predictions",  
            json=payload, 
            headers = {"Accept": "application/json"},
            timeout=timeout, 
        )

#rstrip elimina la barra final de la URL si existe y v1/predictions es el 
#endpoint al que enviamos los datos
#Enviamos los datos a la API mediante POST.
#json= convierte el diccionario a JSON; Accept indica que esperamos JSON.
#timeout evita esperar indefinidamente si la API no responde.
#guardamos la respuesta HTTP para comprobar después si hubo errores.

        response.raise_for_status()

    except requests.HTTPError as exc: #as exc guarda la excepcion
        status_code = (
            exc.response.status_code
            if exc.response is not None
            else None
        )
        raise PredictionClientError(
            "Error HTTP en la peticion",
            status_code = status_code,
        ) from exc #lanza la excepcion conservando la causa original

#raise_for_status() comprueba si la respuesta HTTP indica un error (4xx o 5xx).
#Si hay un error, lo capturamos con except HTTPError.
#Lo convertimos a PredictionClientError y conservamos el status_code
#para saber qué error ha devuelto la API (por ejemplo, 422).

    except requests.Timeout as exc:
        raise PredictionClientError(
            "Tiempo de espera agotado"
        ) from exc

    except requests.ConnectionError as exc:
        raise PredictionClientError(
            "No se ha podido conectar con la API"
        ) from exc

#Si la API tarda demasiado (Timeout) o no podemos conectar (ConnectionError),
#capturamos el error y lo convertimos en PredictionClientError.
#Así distinguimos qué ha fallado y mantenemos una excepción propia del cliente.

    try: 
        data = response.json() #convertimos a json

    except ValueError as exc: #comprobamos que podemos interpretarlo
        raise PredictionClientError(
            "la respuesta no contiene un JSON valido"
        ) from exc

    if not isinstance(data,dict): #comprobar que es un diccionario
        raise PredictionClientError(
            "La respuesta JSON debe ser un objeto"
        )

    return data #devuelve el diccionario

#objeto JSON en python es un dict