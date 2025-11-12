import os
import numpy as np
from scripts.utilitarios.embedding.embedding import generar_embedding  # Usa tu función existente
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
load_dotenv()
# Config DB
VECTORES_CACHE = None
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def elegir_mejor_chunck(pregunta, cantidad_chunks):

    session = SessionLocal()
    
    try:
        embedding = generar_embedding(pregunta)
        
        if isinstance(embedding, np.ndarray):
            embedding = [float(x) for x in embedding]
        
        

        
        query = text("""
            SELECT respuesta, pregunta
            FROM chunks
            ORDER BY embedding <=> (:pregunta)::vector
            LIMIT :cantidad
        """)
       


        resultados = session.execute(
            query,
            {"pregunta":embedding,"cantidad":cantidad_chunks}
        ).fetchall()
        if not resultados:
            return []
        #converir a diccionario
        chunks = [
            {
            "num_video": r.num_video,
            "autor": r.autor,
            "fecha": r.fecha,
            "titulo": r.titulo,
            "tags": r.tags,
            "contenido": r.contenido,
            }
            for r in resultados
        ]

        return chunks


    except Exception as e:
        print(f"❌ Error en buscar_similares: {e}")
        return []
    finally:
        session.close()