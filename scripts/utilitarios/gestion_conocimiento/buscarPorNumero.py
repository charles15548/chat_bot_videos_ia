from scripts.servicios.cruds.chunks.crud import listar_chunks
from openai import OpenAI
from dotenv import load_dotenv
import os
import json

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))




# def capa_filtro_numero_video(pregunta: str) -> str:
#     videos_db = listar_chunks()
#     videos_texto = "\n".join(videos_db) if videos_db else "No hay videos registrados"

#     prompt = f"""
# Modifica la consulta del usuario si el pedido del video es ambiguo.
# Si el usuario pide un video solo por número, agrega después del número el título correspondiente.
# Ejemplo:
# usuario: dame un resumen del video 5
# corrección: dame un resumen del video 5 - El Mundo en 2021

# No agregues comentarios ni explicaciones.
# Solo devuelve la consulta corregida.

# Lista de videos:
# {videos_texto}

# Consulta del usuario:
# {pregunta}
# """

#     response = client.responses.create(
#         model="gpt-4.1-nano",
#         input=prompt
#     )

#     return response.output_text.strip()


def capa_filtro_numero_video(pregunta: str):
    videos_db = listar_chunks()
    videos_texto = "\n".join(videos_db) if videos_db else "No hay videos registrados"

    prompt = f"""
Tu tarea es:
1. Corregir la consulta del usuario si el pedido del video es ambiguo.
2. Identificar qué numero de videos están siendo solicitados.

Devuelve SOLO un JSON con esta estructura EXACTA:
{{
  "consulta": "consulta corregida",
  "lista_videos": ["01", "2", "40"]
}}

Reglas:
- Si no se menciona ningún numero de video, devuelve lista_videos vacía []
- No agregues texto fuera del JSON

Lista de videos:
{videos_texto}

Consulta del usuario:
{pregunta}
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    resultado = json.loads(response.output_text.strip())

    return resultado["consulta"], resultado["lista_videos"]
