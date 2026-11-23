import requests
import os 
from dotenv import load_dotenv

load_dotenv()

url = "https://opendata.aemet.es/opendata/api/valores/climatologicos/inventarioestaciones/todasestaciones"

api_key = os.getenv("AEMET_API_KEY")

params = {
    "api_key": api_key
}

#obtener todas las estaciones meterologicas
def obtener_estaciones():
    url = "https://opendata.aemet.es/opendata/api/valores/climatologicos/inventarioestaciones/todasestaciones"

    respuesta = requests.get(url,params=params)
    respuesta.raise_for_status()

    #la primera respuesta contiene una URL con los datos 
    url_datos = respuesta.json()["datos"]

    #hacemos otra peticion para descargar las estaciones
    respuesta_datos = requests.get(url_datos)
    respuesta_datos.raise_for_status()

    return respuesta_datos.json()

#buscar una estacion por su nombre
def buscar_estacion(estaciones,nombre):
    for estacion in estaciones: 
        if estacion["nombre"] == nombre: 
            return estacion["indicativo"]

    raise ValueError("No se ha encontrado la estacion")

#obtener las climatologias diarias 
def obtener_climatologia(idema, fechaIniStr, fechaFinStr):
    url = f"https://opendata.aemet.es/opendata/api/valores/climatologicos/diarios/datos/fechaini/{fechaIniStr}/fechafin/{fechaFinStr}/estacion/{idema}"

    respuesta = requests.get(url, params=params)
    respuesta.raise_for_status()

    #la primera respuesta contiene una url con los datos 
    url_datos = respuesta.json()["datos"]

    #descargamos los datos de climatología 
    respuesta_datos = requests.get(url_datos)
    respuesta_datos.raise_for_status()

    return respuesta_datos.json()

#programa principal 

#obtener las estaciones
estaciones = obtener_estaciones()

#buscar el indicativo de ciudad universitaria 
idema = buscar_estacion(estaciones, "MADRID, CIUDAD UNIVERSITARIA")
print("Indicativo:", idema)

#fechas de la practica
fechaIniStr = "2019-10-01T00:00:00UTC"
fechaFinStr = "2019-10-30T23:59:59UTC"

#obtener climatologias
climatologias = obtener_climatologia(idema, fechaIniStr, fechaFinStr)

#mostrar los resultados 

for dia in climatologias: 
    print(dia)