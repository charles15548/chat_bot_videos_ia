import os
import json
import numpy as np
import faiss
from scripts.utilitarios.embedding.embedding import generar_embedding

DATA_DIR = "data"
INDEX_DIR = os.path.join(DATA_DIR, "indices")
METADATA_FILE = os.path.join(DATA_DIR, "metadata.json")

FAISS_CACHE = None
META_CACHE = None


def cargar_todos_los_indices():
    """Carga todos los embeddings (.npy) y su metadata."""
    print("📥 Cargando FAISS en memoria...")
    print(f"📂 Ruta embeddings: {os.path.abspath(INDEX_DIR)}")
    print(f"📂 Ruta metadata: {os.path.abspath(METADATA_FILE)}")

    if not os.path.exists(INDEX_DIR):
        raise ValueError(f"⚠️ No existe la carpeta {INDEX_DIR}")

    archivos = [f for f in os.listdir(INDEX_DIR) if f.endswith(".npy")]
    print("📂 Archivos encontrados en indices:", archivos)

    if not archivos:
        raise ValueError("⚠️ No hay embeddings en /data/indices")

    indices = []
    for archivo in archivos:
        ruta = os.path.join(INDEX_DIR, archivo)
        emb = np.load(ruta)
        dim = emb.shape[1]
        index = faiss.IndexFlatL2(dim)
        index.add(emb)
        indices.append(index)
        print(f"✅ {archivo} cargado ({emb.shape[0]} vectores)")

    if not os.path.exists(METADATA_FILE):
        raise ValueError(f"⚠️ No se encontró {METADATA_FILE}")

    with open(METADATA_FILE, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    print(f"✅ {len(indices)} índices cargados correctamente.")
    return indices, metadata


def elegir_mejor_chunck(pregunta: str, cantidad_chunks: int):
    """Busca los chunks más relevantes desde FAISS + metadata.json"""
    global FAISS_CACHE, META_CACHE

    if FAISS_CACHE is None or META_CACHE is None:
        FAISS_CACHE, META_CACHE = cargar_todos_los_indices()

    #  Generar embedding de la pregunta
    embedding = np.array(generar_embedding(pregunta), dtype=np.float32).reshape(1, -1)

    resultados = []

    #  Iterar sobre cada índice y su metadata asociada
    for idx, index in enumerate(FAISS_CACHE):
        distancias, ids = index.search(embedding, cantidad_chunks)
        distancias = distancias.flatten()
        ids = ids.flatten()

        # Obtener video correspondiente
        video_data = META_CACHE["videos"][idx]
        chunks = video_data["chunks"]

        for i, id_chunk in enumerate(ids):
            if id_chunk < len(chunks):
                chunk = chunks[id_chunk]
                resultados.append({
                    "num_video": video_data.get("num_video", ""),
                    "autor": video_data.get("autor", ""),
                    "fecha": video_data.get("fecha", ""),
                    "titulo": video_data.get("titulo", ""),
                    "tags": video_data.get("tags", ""),
                    "contenido": chunk.get("contenido", ""),
                    "distancia": float(distancias[i]),
                    "fuente_indice": idx
                })

    # 🔹 Ordenar por relevancia
    resultados.sort(key=lambda x: x["distancia"])
    mejores = resultados[:cantidad_chunks]

    print(f"🔍 Se encontraron {len(mejores)} chunks relevantes.")
    print(f"{resultados["contenido"]} ")
    return mejores
