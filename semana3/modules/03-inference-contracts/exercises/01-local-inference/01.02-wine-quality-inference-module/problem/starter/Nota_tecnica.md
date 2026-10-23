## Nota técnica — Práctica 3.2

### Responsabilidad de cada módulo

- **contracts.py:** en este archivo he definido los datos de entrada y salida utilizando Pydantic. También he establecido los rangos que pueden tener las variables para evitar que se introduzcan valores incorrectos.

- **preprocess.py:** se encarga de preparar los datos antes de pasarlos al modelo. Para ello, crea un vector con las 11 características del vino, siguiendo siempre el mismo orden.

- **inference.py:** carga el modelo que nos ha proporcionado el profesor y comprueba que tenga las características y los métodos necesarios. Después, utiliza el modelo para obtener la categoría del vino y la confianza de la predicción.

- **predict_file.py:** es el archivo que conecta todo lo anterior. Lee las muestras del CSV, comprueba que sean válidas, realiza las predicciones y guarda los resultados en otro CSV.

### Decisiones de diseño

**1. Validar los datos antes de hacer las predicciones**

He decidido utilizar Pydantic porque permite comprobar fácilmente que los datos tengan los tipos y valores adecuados. Así, si una muestra tiene algún dato incorrecto, podemos detectar el error antes de utilizar el modelo.

También he preferido guardar primero todas las predicciones en una lista y crear el CSV al final. De esta forma, si alguna de las filas falla, no se genera un archivo con solo parte de los resultados.

**2. Mantener el orden de las variables**

He utilizado `FEATURE_NAMES` para asegurarme de que las 11 características se introducen siempre en el mismo orden. Esto es importante porque el modelo espera recibir los datos igual que cuando fue entrenado.

Además, he dejado `sample_id` fuera del vector porque solo sirve para identificar cada muestra y no aporta información para realizar la predicción.