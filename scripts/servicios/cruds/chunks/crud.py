import os
from sqlalchemy import create_engine,text
from dotenv import load_dotenv
from .utils import limpiar_texto
import numpy as np
import numpy as np
from sqlalchemy import text

from scripts.utilitarios.embedding.embedding import generar_embedding


load_dotenv()

DATABASE_URL=os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)






def dividir_en_chunks(texto, palabras_por_chunk=600):
    """
    Divide el texto en partes de aproximadamente 'palabras_por_chunk' palabras.
    Retorna una lista de strings.
    """
    palabras = texto.split()
    chunks = []
    for i in range(0, len(palabras), palabras_por_chunk):
        chunk = " ".join(palabras[i:i + palabras_por_chunk])
        chunks.append(chunk)
    return chunks


def agregar(num_video, autor, fecha, titulo, tags, contenido):
    """
    Divide el contenido en chunks y crea un registro por cada uno,
    repitiendo los metadatos y generando su embedding.
    """
    # Dividimos el contenido largo
    chunks = dividir_en_chunks(contenido, palabras_por_chunk=600)
    print(f"Se generarán {len(chunks)} embeddings para este contenido.")

    with engine.begin() as conn:
        for idx, chunk in enumerate(chunks, start=1):
            chunk_limpio = limpiar_texto(chunk)
            embedding = generar_embedding(chunk_limpio)
            emb = np.array(embedding, dtype=np.float32)

            query = text("""
                INSERT INTO chunks (num_video, autor, fecha, titulo, tags, contenido, embedding)
                VALUES (:num_video, :autor, :fecha, :titulo, :tags, :contenido, :embedding)
                RETURNING id;
            """)

            result = conn.execute(query, {
                "num_video": num_video,
                "autor": autor,
                "fecha": fecha,
                "titulo": titulo,
                "tags": tags,
                "contenido": chunk,
                "embedding": emb.tolist(),
            })
            new_id = result.fetchone()[0]
            print(f"✅ Chunk {idx} insertado con id {new_id}")

#if __name__ == "__main__":
    #editar(1,"Charles huaman llaccta")