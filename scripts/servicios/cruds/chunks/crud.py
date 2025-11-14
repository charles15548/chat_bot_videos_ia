import os
from sqlalchemy import create_engine,text
from dotenv import load_dotenv
from .utils import limpiar_texto
import numpy as np
import numpy as np
from sqlalchemy import text
from scripts.editar_variables import PALABRAS_POR_CHUNK
import json
from scripts.utilitarios.embedding.embedding import generar_embedding


load_dotenv()
DATABASE_URL=os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

DATA_DIR = "/opt/render/project/src/data"
INDEX_DIR = os.path.join(DATA_DIR, "indices")
METADATA_FILE = os.path.join(DATA_DIR, "metadata.json")
os.makedirs(INDEX_DIR, exist_ok=True)



def listar_chunks():
    if not os.path.exists(METADATA_FILE):
        return []
    
    with open(METADATA_FILE, "r",encoding="utf-8") as f:
        metadata = json.load(f)
    videos = metadata.get("videos",[])
    if not videos:
        print("No hay videos")
        return []
    lista_formateada = []
    
    for vid in videos:
        texto = f"-Video: {vid["num_video"]} -Titulo: {vid['titulo']} -Expositor {vid['autor']}"
        lista_formateada.append(texto)
    return lista_formateada
    


def dividir_en_chunks(texto, palabras_por_chunk):
    """
    Divide el texto en partes de aproximadamente 'palabras_por_chunk' palabras.
    Retorna una lista de strings.
    """
    palabras = texto.split()
    chunks = []
    for i in range(0, len(palabras), palabras_por_chunk):
        chunk = " ".join(palabras[i:i + palabras_por_chunk]).strip()
        if chunk:
            chunks.append(chunk)
    return chunks

def contar_tokens(texto):
    return len(texto.split())



def agregar(num_video, autor, fecha, titulo, tags, contenido):
    chunks = dividir_en_chunks(contenido, PALABRAS_POR_CHUNK)

    if chunks and contar_tokens(chunks[-1]) < 200:
        print(f"Último chunk demasiado pequeño ({contar_tokens(chunks[-1])} tokens). No se guardará.")
        chunks = chunks[:-1]

    print(f"Se generarán {len(chunks)} embeddings para este contenido.")

    embeddings = []
    chunk_data = []

    for idx, chunk in enumerate(chunks, start=1):
        chunk_limpio = limpiar_texto(chunk)
        if not chunk_limpio.strip():
            print(f"Chunk {idx} vacío, se omite.")
            continue

        embedding = np.array(generar_embedding(chunk_limpio), dtype=np.float32)
        embeddings.append(embedding)
        chunk_data.append({
            "contenido": chunk_limpio,
            "embedding_index": idx - 1
        })

    index_path = os.path.join(INDEX_DIR, f"{num_video}.index")
    np.save(index_path, np.vstack(embeddings))
    print(f"✅ Embeddings guardados en {index_path}")

    # ---- Metadata ----
    metadata = {"videos": []}
    if os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, "r", encoding="utf-8") as f:
            metadata = json.load(f)

    video_info = {
        "num_video": num_video,
        "autor": autor,
        "fecha": fecha,
        "titulo": titulo,
        "tags": tags,
        "chunks": chunk_data
    }

    metadata["videos"] = [v for v in metadata["videos"] if v["num_video"] != num_video]
    metadata["videos"].append(video_info)

    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    print(f"✅ Metadata actualizada en {METADATA_FILE}")

# def agregar(num_video, autor, fecha, titulo, tags, contenido):
#     """
#     Divide el contenido en chunks y crea un registro por cada uno,
#     repitiendo los metadatos y generando su embedding.
#     """
#     contenido_completo = " ".join(map(str, [contenido, num_video, autor, fecha, titulo, tags]))
#     chunks = dividir_en_chunks(contenido_completo, PALABRAS_POR_CHUNK)

#     if chunks and contar_tokens(chunks[-1]) < 200:
#         print(f"Ultimo chunk demasiado pequeño ({contar_tokens(chunks[-1])} tokens). No se guardará.")
       
#         chunks = chunks[:-1]
#     print(f"Se generarán {len(chunks)} embeddings para este contenido.")

#     with engine.begin() as conn:
#         for idx, chunk in enumerate(chunks, start=1):
#             chunk_limpio = limpiar_texto(chunk)
#             if not chunk_limpio.strip():
#                 print(f"Chunk {idx} vacio, se omite")
#                 continue
#             embedding = generar_embedding(chunk_limpio)
#             emb = np.array(embedding, dtype=np.float32)

#             query = text("""
#                 INSERT INTO chunks (num_video, autor, fecha, titulo, tags, contenido, embedding)
#                 VALUES (:num_video, :autor, :fecha, :titulo, :tags, :contenido, :embedding)
#                 RETURNING id;
#             """)

#             result = conn.execute(query, {
#                 "num_video": num_video,
#                 "autor": autor,
#                 "fecha": fecha,
#                 "titulo": titulo,
#                 "tags": tags,
#                 "contenido": chunk,
#                 "embedding": emb.tolist(),
#             })
#             new_id = result.fetchone()[0]
#             print(f"✅ Chunk {idx} insertado con id {new_id}")


# def eliminar(id:int):
#     with engine.connect() as conn:
#         result = conn.execute(text("DELETE FROM chunks WHERE id = :id RETURNING id"),{"id":id})
#         conn.commit()
#         deleted = result.fetchone()
#         if deleted:
#             print(f"🗑️ Persona con ID {id} eliminada correctamente.")
#         else:
#             print(f"⚠️ No se encontró ninguna Archivo con ID {id}.")

def eliminar_video(num_video):
   

    # 1) Verificar metadata.json
    if not os.path.exists(METADATA_FILE):
        print("⚠️ No existe metadata.json, no hay nada que borrar.")
        return

    with open(METADATA_FILE, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    videos = metadata.get("videos", [])

    # Buscar si existe
    video_existente = next((v for v in videos if v["num_video"] == num_video), None)

    if not video_existente:
        print(f"⚠️ No se encontró el video {num_video} en metadata.json.")
        return

    # 2) Borrar el archivo .index
    index_path = os.path.join(INDEX_DIR, f"{num_video}.index")
    if os.path.exists(index_path):
        os.remove(index_path)
        print(f"🗑️ Archivo index eliminado: {index_path}")
    else:
        print(f"⚠️ No se encontró el archivo index para el video {num_video}")

    # 3) Quitar del metadata.json
    metadata["videos"] = [v for v in videos if v["num_video"] != num_video]

    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    print(f"✅ Video {num_video} eliminado del metadata.json")



if __name__ == "__main__":
    listar_chunks()