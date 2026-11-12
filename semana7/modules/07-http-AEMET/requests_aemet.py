import requests

url = "https://opendata.aemet.es/opendata/api/valores/climatologicos/inventarioestaciones/todasestaciones"

api_key = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJjbGF1ZGlhc2FuenNyQGdtYWlsLmNvbSIsImp0aSI6IjIzOTgwZDYzLWIxNzYtNDhlYi05MzRjLTlmZDhkMGY5N2Q4OSIsImV4cCI6MTgwMTI0NzkwNCwiaXNzIjoiQUVNRVQiLCJpYXQiOjE3OTI2MDc5MDQsInVzZXJJZCI6IjIzOTgwZDYzLWIxNzYtNDhlYi05MzRjLTlmZDhkMGY5N2Q4OSIsInJvbGUiOiIifQ.2-1ADIvgt4Z0eJFwwtB6P8Kntr-sVaW3ce9sDlcf0Xo"

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