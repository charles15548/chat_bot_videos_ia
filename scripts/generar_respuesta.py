import json
import openai
from dotenv import load_dotenv
import os
#from scripts.utilitarios.gestion_conocimiento.agente_selector import elegir_mejor_chunck
from scripts.utilitarios.gestion_conocimiento.selector import elegir_mejor_chunck
from scripts.utilitarios.prompts.promt import prompt_base
from scripts.editar_variables import MODELO,CHUNCKS_POR_DOCUMENTO
from scripts.servicios.cruds.chunks.crud import listar_chunks

import re
# Cargar clave desde .env
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Cliente de OpenAI
from openai import OpenAI
client = OpenAI()





# def generar_respuesta_stream(pregunta_usuario, historial):
    
#     chunks = elegir_mejor_chunck(pregunta_usuario,CHUNCKS_POR_DOCUMENTO)

#     contexto = "\n\n".join([f"""Num° Video:{c['num_video']} \n 
# Autor:{c['autor']} \n
# Fecha:{c['fecha']} \n
# Titulo:{c['titulo']} \n 
# Contenido:{c['contenido']} \n""" for c in chunks])
#     print(contexto)
#     modelo = MODELO
#     prompt = prompt_base()

#     if chunks == []:
#         mensajes = [
#             {
#                 "role": "system",
#                 "content": "Responde exactamente: Lo siento, aún no tengo información sobre ello"
#             }
#         ]
#     else:
        

#         mensajes = [
#             {
#                 "role": "system",
#                 "content": prompt  + f"\n Información: \n{contexto}"
#             }
#         ]

#     mensajes.extend({
#         "role": "user" if msg.rol == "user" else "assistant",
#         "content": msg.contenido
#     } for msg in historial)

#     # Generator para streaming
#     def event_generator():
#         with client.chat.completions.stream(model=modelo, messages=mensajes) as stream:
#             for event in stream:
#                 if hasattr(event, "delta") and event.delta:
#                     yield json.dumps({"contenido": event.delta}) + "\n"

#     return event_generator



def generar_respuesta_stream(pregunta_usuario, historial):
    ultimo_mensaje_bot = None
    if historial and historial[-1].rol == "assistant":
       ultimo_mensaje_bot = historial[-1].contenido
    else:
        ultimo_mensaje_bot = ""
    print("Ultimo mensaje del bot: ",ultimo_mensaje_bot)
    chunks = elegir_mejor_chunck(pregunta_usuario,ultimo_mensaje_bot, CHUNCKS_POR_DOCUMENTO)
    videos_db = listar_chunks()
    if not chunks:
        mensajes = [{
            "role": "system",
            "content": "Responde exactamente: Lo siento, aún no tengo información sobre ello"
        }]
    else:
        contexto = "\n\n".join([
            f"""Num° Video:{c['num_video']} \nAutor:{c['autor']} \nFecha:{c['fecha']} \nTitulo:{c['titulo']} \nContenido:{c['contenido']}"""
            for c in chunks
        ])
        
        videos_texto = "\n".join(videos_db) if videos_db else "No hay videos registrados"
        prompt = prompt_base()
        mensajes = [{
            "role": "system",
            "content": prompt + f"\n Información: \n{contexto} \n Videos disponibles actualmente en db(de estos videos sacas fracmentos de informacion en cada consulta, mostrarlos de forma numerada): {videos_texto}"
        }]
        
        print("\n📹 Lista de videos:\n")
        print(f"\n {videos_texto}")
        

    mensajes.extend({
        "role": "user" if msg.rol == "user" else "assistant",
        "content": msg.contenido
    } for msg in historial)

    def event_generator():
        with client.chat.completions.stream(model=MODELO, messages=mensajes) as stream:
            for event in stream:
                if hasattr(event, "delta") and event.delta:
                    yield json.dumps({"contenido": event.delta}) + "\n"

    return event_generator

