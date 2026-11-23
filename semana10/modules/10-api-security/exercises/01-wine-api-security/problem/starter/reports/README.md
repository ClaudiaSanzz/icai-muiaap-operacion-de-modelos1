# S10.7 — Informe de carga

> **TODO S10.7c:** ejecuta Locust con `--csv reports/s10`, versiona los CSV
> generados y completa las tablas y el análisis de este archivo.

Plantilla del informe. Rellénala con **tus** resultados: dependen de la máquina,
del número de workers y de la configuración de `.env`. No copies cifras de otra
persona ni de la solución, que no incluye resultados.


# S10.7 — Informe de carga

## Cómo se ha medido

| Dato | Valor |
| --- | --- |
| Comando de la API | `uv run fastapi dev src/wine_api/main.py` (1 proceso) |
| Comando de Locust | `uv run --group load locust -f locustfile.py --headless -u 20 -r 5 -t 1m --host http://127.0.0.1:8000 --csv reports/s10` |
| Cliente usado | `front` |
| `rate_limit_per_minute` del cliente | 10000 |
| Máquina | Windows, Intel(R) Core(TM) Ultra 7 155H |

Archivos generados por Locust y versionados junto a este informe:
`s10_stats.csv`, `s10_failures.csv` y `s10_stats_history.csv`.

## Resultados

Los valores se han obtenido del archivo `s10_stats.csv`, generado al ejecutar la prueba de carga con Locust.

| Endpoint | Peticiones | RPS | p50 (ms) | p95 (ms) | Fallos | % 429 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `POST /v1/predictions` | 752 | 12,73 | 7 | 11 | 0 | 0 % |
| `/v1/predictions [422]` | 89 | 1,51 | 7 | 11 | 0 | — |
| `GET /health` | 90 | 1,52 | 5 | 7 | 0 | — |
| Aggregated | 931 | 15,77 | 7 | 11 | 0 | 0 % |

`% 429` = fallos `429` de `s10_failures.csv` / peticiones de
`POST /v1/predictions` × 100.

## Análisis (5–10 líneas)

- **¿Cuántas predicciones por minuto deja pasar el límite y cuántas ha pedido Locust? ¿Cuadra el `% 429` con esa cuenta?**

  En esta prueba he configurado un límite de 10000 peticiones por minuto para el cliente `front`. Locust ha realizado 752 predicciones válidas y 89 inválidas, es decir, 841 peticiones al endpoint de predicción durante la prueba de un minuto. Como no se ha alcanzado el límite, no se han producido errores 429. Por tanto, el porcentaje del 0 % es coherente con la configuración utilizada.

- **¿Qué latencia (p50, p95) tiene `GET /health`, que no pasa por autenticación ni rate limit, frente a `POST /v1/predictions`?**

  El endpoint `/health` presenta una latencia menor, con un p50 de 5 ms y un p95 de 7 ms. En cambio, `/v1/predictions` tiene un p50 de 7 ms y un p95 de 11 ms. Esto tiene sentido porque las predicciones requieren autenticación, comprobación del límite de peticiones y ejecución del modelo.

- **¿Qué cambiaría con dos workers (`fastapi run --workers 2`) y un contador en memoria por proceso?**

  Si utilizáramos dos workers, cada proceso tendría su propio contador de peticiones en memoria. Como estos contadores no se comparten, el límite de peticiones podría superarse globalmente. Para evitarlo, sería necesario utilizar un almacenamiento compartido, como Redis.

- **Si quisieras medir la capacidad del servicio y no la política de cuotas, ¿qué cliente y qué límite usarías?**

  Utilizaría un cliente específico para las pruebas de carga, con el permiso `predict` y un límite de peticiones suficientemente alto para que el rate limiting no afectara a los resultados. Así podría medir el rendimiento de la API y los tiempos de respuesta sin que las peticiones fueran rechazadas por la cuota.
