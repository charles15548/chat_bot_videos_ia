from fastapi import FastAPI, HTTPException,Form,File,Body,UploadFile
from pydantic import BaseModel
from datetime import datetime
from scripts.generar_respuesta import generar_respuesta_stream
from scripts.servicios.cruds.personas.crud import acceso
from scripts.servicios.cruds.chunks.crud import agregar
import uvicorn
import markdown2
from bs4 import BeautifulSoup
#puede ir en otro achivo ====
from typing import List, Literal, Optional
from fastapi.middleware.cors import CORSMiddleware
#puede ir en otro achivo ====
from dotenv import load_dotenv
import openai
import os
from io import BytesIO 
from pathlib import Path
import shutil
from fastapi.responses import JSONResponse

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
# Inicializar FastAPI
app = FastAPI(title="API RAG - Soporte Técnico")


BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # desde app.py


UPLOAD_DIR = Path("imagen")
UPLOAD_DIR.mkdir(exist_ok=True)

origins = [
    "http://localhost:3000",              
    "https://soporte2.intelectiasac.com", 
    "https://ipp.intelectiasac.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Mensaje(BaseModel):
    rol: Literal["user", "bot"]
    contenido: str
# Modelo para recibir pregunta
class PreguntaEntrada(BaseModel):
    pregunta: str
    historial: List[Mensaje]
# Modelo de respuesta
class RespuestaSalida(BaseModel):
    respuesta: str




from fastapi.responses import StreamingResponse

@app.post("/consultar-stream")
def consultar_stream(pregunta_entrada: PreguntaEntrada):
    try:
        pregunta = pregunta_entrada.pregunta
        historial = pregunta_entrada.historial

        generator = generar_respuesta_stream(pregunta, historial)
        
        return StreamingResponse(generator(), media_type="text/event-stream")
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


    



@app.post("/acceso")
async def log(
    correo: str = Form(...),
    contrasena: str= Form(...),
    

):
    user = acceso(correo,contrasena)
    return user






@app.post("/subir-informacion")
async def subir_archivo(
    num_video: str = Form(...),
    autor: str = Form(...),
    fecha: str = Form(...),
    titulo: str = Form(...),
    tags: str = Form(...),
    contenido: str = Form(...),
    link: str = Form(...),
):
    try:
        
        agregar(num_video, autor, fecha, titulo,tags,contenido,link)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))



# Ejecutar: uvicorn app:app --reload
if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
