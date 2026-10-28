from fastapi import APIRouter, Depends

from app.schemas.chat import ChatEntrada, ChatSalida
from app.services.llm import get_llm
from app.services.orquestador import responder

router = APIRouter()

#AQUI RECIBE MENSAJES DEL USUARIO, SE LOS PASA AL LLM Y UTILIZA
#EL ORQUESTADOR QUE HEMOS PROGRAMADO.

# TODO: POST /chat (entrada ChatEntrada, salida ChatSalida). Recibe el LLM con Depends(get_llm)

@router.post("/chat", response_model = ChatSalida)
def chat(entrada: ChatEntrada, llm=Depends(get_llm)):
    return responder(entrada.mensajes, llm)

#con los mensajes de entrada le decimos a FastApi que nos consiga
#el LLM usando la funcion get_llm

#recibe la conversacion, llama a responder() y devuelve el resutlado 
#llm=Depends(get_llm) significa FastAPI, cuando alguien llame a /chat, utiliza get_llm() 
# para obtener el LLM y pásamelo en la variable llm.

#cuando un usuario escirbe en nuestro chatbot :
#1. el usario envia un mensaje POST/chat 
#2. FASTapi ejecuta get_llm() obtiene el llm que vamos a utilizar
#3. FastApi llama a chat(), le pasa los mensajes y el llm
#4. responder(entrada.mensajes, llm), el prquestador utiliza ese LLM