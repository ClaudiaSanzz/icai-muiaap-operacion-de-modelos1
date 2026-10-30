from fastapi import APIRouter

from app.schemas.prestamo import PrediccionSalida, PrestamoEntrada
from app.services.modelo import predecir

router = APIRouter()

#AQUI RECIBE DIRECTAMENTE LOS 6 DATOS Y CALCULA EL RIESGO

# TODO: POST /predict (entrada PrestamoEntrada, salida PrediccionSalida)

#FastApi cuando alguien haga una peticion POST a /predict, ejecuta la funcion
#que esta debajo 

@router.post("/predict", response_model=PrediccionSalida)
def predict(entrada:PrestamoEntrada): 
    return predecir(entrada)
    
#@router.post indica que recibimos una peticion POST
#/predict es el nombre de la ruta 
#response_model = PrediccionSalida indica como tiene que ser el resultado
#la entrada tiene que cumplir las reglas que definimos en prestamo.py
#luego con el return coge los datos que hemos recibido, los pasa a nuestra 
#funcion predecir() y devuelve el resultado


#predecir () calcula el riesgo
#predict () permite calcularlo mediante HTTP