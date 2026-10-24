### Puente al contrato Wine

Al pasar de Churn a Wine mantendríamos la misma estructura: formulario, botón de envío, predicción y presentación de resultados.

Lo que cambiaría serían los datos que introducimos y el resultado que devuelve el modelo. En Churn utilizamos información de los clientes para predecir si se darán de baja, mientras que en Wine utilizaríamos las características del vino para clasificar su calidad.

En ambos casos, la predicción solo se ejecutaría al pulsar el botón y los posibles errores se mostrarían mediante un mensaje comprensible.

Por tanto, podríamos reutilizar la estructura de la aplicación, adaptando los widgets y la salida al contrato de Wine, sin modificar la lógica del modelo.