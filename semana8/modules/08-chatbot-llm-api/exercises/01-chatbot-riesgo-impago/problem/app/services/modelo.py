import joblib

from app.config import MODEL_PATH
from app.schemas.prestamo import PrediccionSalida

#2. AQUI CARGAMOS EL MODELO Y PREDECIMOS 

# Orden en el que el modelo espera las variables
VARIABLES = [
    "edad",
    "ingresos_mensuales",
    "importe_prestamo",
    "plazo_meses",
    "antiguedad_laboral_anios",
    "impagos_previos",
]

# TODO: cargar el modelo joblib una sola vez, al importar el modulo
# TODO: funcion decidir(probabilidad) -> "aprobar", "revisar" o "rechazar" (umbrales en el enunciado)
# TODO: funcion predecir(entrada) -> PrediccionSalida, usando VARIABLES para ordenar los valores

modelo = joblib.load(MODEL_PATH)

#decidir segun la probabilidad 
def decidir(probabilidad):
    if probabilidad < 0.2: 
        return "aprobar"
    elif probabilidad < 0.5:
        return "revisar"
    else: 
        return "rechazar"

#realizamos la predicion 
def predecir(entrada: PrestamoEntrada) -> PrediccionSalida:
    #obtengo los 6 valores de entrada en el orden que espera el modelo
    valores = [getattr(entrada, variable) for variable in VARIABLES] 
    #predict_proba calcula las probabilidades, [0] selcciona la primera solicitud
    #[1] selecciona la probailidad de impago 
    probabilidad = float(modelo.predict_proba([valores])[0][1])

    return PrediccionSalida(
        probabilidad_impago=probabilidad,
        decision=decidir(probabilidad),
    )


