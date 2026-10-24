## Ejecución de la aplicación

Para esta práctica hemos creado una interfaz con Streamlit que permite utilizar el modelo de predicción de calidad del vino de la semana 4.

Primero instalamos las dependencias desde la carpeta `starter`:

```bash
uv sync
```

Después configuramos la variable `MODEL_UI_BUNDLE` para indicar dónde está guardado el modelo de la semana 4:

```bash
export MODEL_UI_BUNDLE="$HOME/master/repos/icai-muiaap-operacion-de-modelos1/semana4/models/wine_quality_bundle"
```

Por último, ejecutamos la aplicación:

```bash
uv run --with 'streamlit>=1.40,<2.0' streamlit run app.py
```

La aplicación muestra un formulario con las 11 características del vino. Podemos modificar sus valores y, al pulsar **Ejecutar inferencia**, obtenemos la clasificación del vino, la confianza de la predicción y las versiones del modelo y del preprocesado.

También hemos comprobado que, si no se encuentra el bundle, aparece un mensaje de error en lugar de detenerse la aplicación.

## Limitaciones y mejoras para la semana 6

Por ahora, la aplicación es bastante básica. Podemos introducir los datos y obtener una predicción, pero no tenemos un historial donde consultar los resultados anteriores.

Además, todavía no utilizamos `st.session_state` para gestionar el estado de la aplicación. Esto se trabajará en la semana 6, donde podremos guardar las predicciones realizadas y mejorar la forma en la que se mantiene la información al interactuar con la interfaz.