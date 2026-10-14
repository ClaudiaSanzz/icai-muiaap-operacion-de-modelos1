# Wine Quality Project

Este proyecto corresponde a la práctica de la semana 2 de Operación de Modelos.

El objetivo de la práctica es convertir los archivos iniciales proporcionados en `starter` en un proyecto Python gestionado con `uv`, de forma que otra persona pueda instalar las dependencias, ejecutar el entrenamiento y revisar el proyecto de manera reproducible.

## Estructura del proyecto

La estructura principal del proyecto es:

    wine-quality-project/
    ├── data/
    │   └── raw/
    │       └── WineQT.csv
    ├── src/
    │   └── wine_quality/
    │       ├── __init__.py
    │       └── train.py
    ├── tests/
    │   └── test_train.py
    ├── pyproject.toml
    ├── uv.lock
    └── README.md

El fichero `WineQT.csv` contiene los datos utilizados para entrenar el modelo.

El código de entrenamiento se encuentra en `src/wine_quality/train.py` y los tests están en `tests/test_train.py`.

## Instalación

Para instalar el proyecto es necesario tener `uv` instalado.

Desde la carpeta `wine-quality-project` se ejecuta:

    uv sync --locked

Este comando instala las dependencias utilizando las versiones definidas en `uv.lock`.

Las dependencias principales del proyecto son:

- pandas
- scikit-learn

Además, como dependencias de desarrollo se utilizan:

- pytest
- ruff

## Ejecutar el entrenamiento

El entrenamiento se ejecuta como un módulo de Python con:

    uv run --frozen python -m wine_quality.train

El script utiliza el fichero de datos situado en:

    data/raw/WineQT.csv

## Ejecutar los tests

Para ejecutar los tests del proyecto:

    uv run --frozen pytest

Esto permite comprobar que el código funciona correctamente después de realizar los cambios.

## Comprobar el código con Ruff

Para revisar posibles errores o problemas de estilo se utiliza Ruff:

    uv run --frozen ruff check

## Comprobaciones realizadas

Antes de realizar la entrega se ejecutaron las siguientes comprobaciones:

    uv sync --locked
    uv run --frozen python -m wine_quality.train
    uv run --frozen pytest
    uv run --frozen ruff check

Se comprobó que:

- `uv sync --locked` instala correctamente las dependencias del proyecto usando el archivo `uv.lock`.
- El entrenamiento arranca correctamente ejecutando `wine_quality.train` como módulo.
- El archivo `WineQT.csv` se carga desde la ruta `data/raw/WineQT.csv`.
- Los tests se ejecutan correctamente con `pytest`.
- Ruff permite revisar posibles errores de estilo o calidad del código.
- El proyecto puede ejecutarse de forma reproducible utilizando las versiones bloqueadas en `uv.lock`.

## Rama de trabajo

La práctica se ha desarrollado en la rama:

    feature/s2-wine-project

La entrega se realiza mediante una Pull Request desde esta rama hacia `main` dentro del mismo fork.