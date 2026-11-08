import json

from pydantic import ValidationError

from app.schemas.chat import ChatSalida, HerramientaUsada
from app.schemas.prestamo import PrestamoEntrada
from app.services.modelo import predecir

#3. AQUI CONECTAMOS EL LLM CON EL MODELO 

NOMBRE_TOOL = "calcular_riesgo_impago"
MAX_VUELTAS = 4 

SISTEMA = (
    "Eres un asistente de riesgo de un banco. Cuando tengas todos los datos de una solicitud de "
    "prestamo, llama a la herramienta calcular_riesgo_impago. Si falta algun dato, pidelo. "
    "Nunca inventes valores. Responde en espanol y de forma breve."
)


def leer_argumentos(texto):
    """YA HECHO: convierte el texto JSON de la tool en dict ({} si no es JSON valido)."""
    try:
        datos = json.loads(texto)
    except (json.JSONDecodeError, TypeError):
        return {}
    if isinstance(datos, dict):
        return datos
    return {}


# TODO: definir_tool() -> dict con la definicion de la tool, sacando "parameters" de PrestamoEntrada
# TODO: ejecutar_tool(nombre, argumentos_json) -> dict con "ok" True/False
#       (tool desconocida, JSON roto, datos invalidos o campos inventados -> ok False con el error)
# TODO: responder(mensajes, llm) -> ChatSalida, con el bucle LLM -> tool -> LLM (maximo MAX_VUELTAS)


#PrestamoEntrada define que datos necesitamos y model_json_schema() se los de describe
#automaticamente al LLM, sin tener que escribri las seis variables del contrato otra vez
#asi si mañana queremos cambiar el limite de edad de 75 a 80 años con el model_json_schema()
#solo cambiamos prestamo.py y no orquestador tambien 

#aqui le explicamos al LLM commo utilizar nuestra funcion. esto es porque el LLM no conoce
#automaticamente nuestras clases de Python.  
def definir_tool():
    return {
        "type" : "function",
        "function": {
            "name" : NOMBRE_TOOL,
            "description" : "Calcula el riesgo de impago de un prestamo",
            "parameters": PrestamoEntrada.model_json_schema(),
        },
    }

def ejecutar_tool(nombre, argumentos_json):
    if nombre != NOMBRE_TOOL:
        return {"ok": False, "error": "Herramienta desconocida"}

    try: 
        #conviero el json recibido en un diccionario de Python
        datos = leer_argumentos(argumentos_json) 
        #comprueba que tenemos los seis datos y que cumplen las reglas
        entrada = PrestamoEntrada(**datos) 
        #llama al mmodelo de modelo.py que acabamos de implementar
        resultado = predecir(entrada)

        #devuelve un diccionario con ok = true, la probabilidad y la decision. 
        return {"ok" : True, **resultado.model_dump()} 

    #si los datos son invalidso, el except devuelve ok = False con el error, en lugar
    #de interrumpir el chatbot. 
    except (ValidationError, TypeError, ValueError) as error: 
        return {"ok": False, "error": str(error)}


def responder(mensajes, llm) -> ChatSalida: 
    #Añadimos las instrucciones del sistema para indicarle al LLM como debe comportarse
    historial = [{"role": "system", "content": SISTEMA}]

    #añadimos los mensajes del usuario. usamos model.dump() porque mensaje es una clase 
    #pydantic y LLM espera diccionarios
    for mensaje in mensajes: 
        historial.append(mensaje.model_dump())

    #Inicializamos la variable antes del bucle
    herramienta_usada = None

    #como max_vueltas=4, permitimos un maximo de 4 vueltas. esto es para limitar las llamadas
    #al LLM y evitar que siga solicitando herramientas indefinidamente
    for i in range(MAX_VUELTAS):
        #llamamos al llm y le pasamos el historial (toda la conver que hemos tenido hasta ahota)
        #y definir_tool() la lista de herramientas que tiene disponibles 
        respuesta = llm.completar(historial, [definir_tool()]) 
        historial.append(respuesta) #guardamos la respuesta del LLM en el historial 
        #de la conversacion

        #RECUERDA QUE RESPUESTA ES UN DICCIONARIO QUE NOS DEVUELVE EL LLM
        #queremos saber dos cosas: 
        #¿el llm nos ha contestado? ¿o nos esta pidiendo que ejecutemos nuestro modelo de prediccion?

        #tool-calls = None porque no hay ninguna clave llamada asi
        #get busca una clave dentro de un diccionario

        llamadas = respuesta.get("tool_calls") #miramos si el LLM ha podido usar una herramienta
        if llamadas is None or llamadas == []: #si no ha pedido ninguna, entramos en el if
            texto = respuesta.get("content") #recogemos lo que ha escrito el llm

            if texto is None:
                texto = "" #si texto no tiene ningun valor le asignamos un texto vacio

            return ChatSalida(
                respuesta = texto,
                herramienta=herramienta_usada,
            )

        #cuando quiere LLM utilizar una herramietna
        for llamada in respuesta["tool_calls"]:
            nombre = llamada["function"]["name"]
            argumentos_json = llamada["function"]["arguments"]
            #hemos separado el nombre de la herramietna y los datos que necesita
            #ejecutamos la herramienta

            resultado = ejecutar_tool(nombre, argumentos_json)

            #guardamos la herramienta usada
            herramienta_usada = HerramientaUsada(
                nombre = nombre,
                argumentos = leer_argumentos(argumentos_json),
                resultado=resultado,
            )

            #añadimos el resultado al historial
            historial.append({
                "role": "tool",
                "tool_call_id" : llamada["id"],
                "content": json.dumps(resultado),
            })

        #cuando termina este for, volvemos al bucle principal. ahora el llm recibe el
        #historial actualizado que incluye la prediccion

    #si hemos pasado al limte de vueltas y no hemos consguido una respuesta final devolvemos:
    return ChatSalida(
        respuesta= "No he podido completar la solicitud",
        herramienta = herramienta_usada,
    )

