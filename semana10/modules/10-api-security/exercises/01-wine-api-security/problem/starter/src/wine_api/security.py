"""Autenticación por API key y autorización por scopes.

- Autenticación (401): ¿quién llama? La clave de `X-API-Key` debe coincidir con
  la de algún cliente configurado.
- Autorización (403): ¿qué puede hacer? El cliente debe tener el scope que
  exige el router.

La clave nunca se devuelve ni se registra en los logs.
"""

import logging
import secrets  # noqa: F401 - pista para S10.2e
from collections.abc import Callable
from dataclasses import dataclass
from typing import Annotated

from fastapi import Security
from fastapi.security import APIKeyHeader  # noqa: F401 - pista para S10.2d

from wine_api.dependencies import RequestIdDep, SettingsDep
from wine_api.errors import AuthenticationError, PermissionDeniedError
from wine_api.settings import Scope

logger = logging.getLogger("wine_api.security")

API_KEY_HEADER = "X-API-Key"
api_key_header = APIKeyHeader(
    name=API_KEY_HEADER,
    auto_error=False,
    description="API key para autenticar al cliente",
)

# TODO S10.2d: declara `api_key_header`, el esquema de seguridad que lee la
# cabecera `API_KEY_HEADER`. Investiga `APIKeyHeader` y su parámetro
# `auto_error`: si lo dejas en `True`, FastAPI responde por ti con su propio
# error y se rompe el sobre `ErrorResponse`. Añade una `description` para
# Swagger. Comprobación: /docs muestra el botón «Authorize».


@dataclass(frozen=True)
class AuthenticatedClient:
    """Cliente ya autenticado. No guarda la clave: no la necesita nadie más."""

    name: str
    scopes: frozenset[str]
    rate_limit_per_minute: int


def authenticate_client(
    settings: SettingsDep, request_id: RequestIdDep, api_key:Annotated[str|None, Security(api_key_header)],
) -> AuthenticatedClient:
    """Identifica al cliente por su API key o lanza `AuthenticationError`."""

    # TODO S10.2e: recibe la clave con un parámetro anotado con
    # `Security(api_key_header)` (puede llegar `None`) y búscala entre
    # `settings.clients`:
    # - compara con `secrets.compare_digest`, nunca con `==`: ¿qué información
    #   filtra una comparación que se para en el primer carácter distinto?
    #   Ojo: con `str` solo admite ASCII; compara bytes (`.encode()`).
    # - si coincide, devuelve un `AuthenticatedClient` con nombre, scopes y
    #   cuota del cliente.
    # - si falta o no coincide, registra el intento con `logger.warning` (con
    #   el `request_id`, NUNCA con la clave) y lanza `AuthenticationError`.
    # Comprobación: uv run pytest -q tests/test_s10_2_authentication.py
        
    #recorremos los clientes configurados
    for name, client in settings.clients.items():

        #comparamos la clave recibida con la guardada
        if api_key is not None and secrets.compare_digest(
            api_key.encode(),
            #recupera la clave que estaba protegida por SecretStr
            client.key.get_secret_value().encode() 
        ):
            return AuthenticatedClient(
                name=name, 
                scopes=frozenset(client.scopes),
                rate_limit_per_minute=client.rate_limit_per_minute,
            )
    #si no encontramos ninguna clase valida
    logger.warning("Intento de autenticacion fallido: %s", request_id)
    raise AuthenticationError() #devuelve un error 401 si la clave no es valida



ClientDep = Annotated[AuthenticatedClient, Security(authenticate_client)]


def require_scope(scope: Scope) -> Callable[..., AuthenticatedClient]:
    """Crea una dependencia que exige `scope`; se declara en el `APIRouter`."""

    # TODO S10.3b: devuelve una función interna que reciba `client: ClientDep`
    # y lance `PermissionDeniedError` si `scope` no está en `client.scopes`.
    # Es una «factoría de dependencias»: `require_scope("admin")` devuelve la
    # dependencia que luego se usa en `dependencies=[Depends(...)]`.
    # ¿Por qué falta de scope es 403 y no 401?
    # Comprobación: uv run pytest -q tests/test_s10_3_authorization.py
        
    # Comprobamos si el cliente tiene el permiso necesario
    def comprobar_permiso(client: ClientDep) -> AuthenticatedClient:
        if scope not in client.scopes:
            raise PermissionDeniedError()

        return client

    # Devolvemos la función que comprobará los permisos
    return comprobar_permiso

#porque es 403 y no 401?
#proque el cliente ya esta identificado mediante su API key (autenticacion),
#pero no tiene permiso para realizar esa operacion (autorizacion)
