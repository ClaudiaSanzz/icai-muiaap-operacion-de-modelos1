## Práctica 6.2 — Streamlit avanzado

En esta práctica hemos continuado con la aplicación de la semana 5, manteniendo el formulario que ya teníamos y añadiendo nuevas funciones para mejorar su funcionamiento.

Hemos utilizado `st.session_state` para que no se pierda la última predicción cuando se actualiza la aplicación y `st.cache_resource` para evitar cargar el gateway cada vez.

También hemos añadido los estados `idle`, `loading`, `success` y `error`, para que el usuario pueda saber qué está pasando mientras se realiza una predicción. Además, ahora podemos reintentar una petición si falla o limpiar el último resultado.

Por otro lado, hemos incorporado la telemetría para llevar un registro de las predicciones realizadas, los errores y los tiempos de respuesta, sin guardar los datos introducidos en el formulario.

Para la semana 7 mantendremos el formulario y la gestión de estados. La principal diferencia será que utilizaremos un gateway HTTP en lugar del gateway local.