### Nota de compatibilidad — Semana 9

En esta semana hemos mejorado la API sin cambiar los endpoints que teníamos en S7 (`POST /v1/predictions` y `GET /health`).

Hemos añadido el campo `served_at` y mejorado cómo se devuelven los datos, cómo se gestionan los errores y la documentación de Swagger.

Añadir `served_at` es un cambio compatible porque los clientes anteriores pueden seguir funcionando igual, utilizando los campos que ya tenían.

Sin embargo, si eliminamos un campo o cambiamos su nombre, podríamos provocar errores en los clientes que ya utilizan la API.

Por eso, al añadir funcionalidades compatibles aumentamos la versión MINOR, pasando de `1.0.0` a `1.1.0`.

Si hiciéramos un cambio que rompiera la compatibilidad, tendríamos que aumentar la versión MAJOR, por ejemplo, a `2.0.0`.