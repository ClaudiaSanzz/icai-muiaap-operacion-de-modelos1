import requests
import os 
from dotenv import load_dotenv

load_dotenv()

url = "https://opendata.aemet.es/opendata/api/valores/climatologicos/inventarioestaciones/todasestaciones"

api_key = os.getenv("AEMET_API_KEY")
print(api_key)
"""
params = {
    "api_key": api_key
}

respuesta = requests.get(url,params=params)

print(respuesta.status_code)
print(respuesta.json())

idema = "3194U"
fechaIniStr = "2019-10-01T00:00:00UTC"
fechaFinStr = "2019-10-30T23:59:59UTC"

url_diaria = f"https://opendata.aemet.es/opendata/api/valores/climatologicos/diarios/datos/fechaini/{fechaIniStr}/fechafin/{fechaFinStr}/estacion/{idema}"

respuesta = requests.get(url_diaria,params=params)

print(respuesta.status_code)
print(respuesta.json())
"""