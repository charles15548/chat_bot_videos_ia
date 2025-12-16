from scripts.servicios.cruds.chunks.crud import listar_chunks
from openai import OpenAI
from dotenv import load_dotenv
import os
import json

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))




def capa_filtro_numero_video(pregunta: str) -> str:
    videos_db = listar_chunks()
    videos_texto = "\n".join(videos_db) if videos_db else "No hay videos registrados"

    prompt = f"""
Modifica la consulta del usuario si el pedido del video es ambiguo.
Si el usuario pide un video solo por número, agrega después del número el título correspondiente.
Ejemplo:
usuario: dame un resumen del video 5
corrección: dame un resumen del video 5 - El Mundo en 2021

No agregues comentarios ni explicaciones.
Solo devuelve la consulta corregida.

Lista de videos:
{videos_texto}

Consulta del usuario:
{pregunta}
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    return response.output_text.strip()
