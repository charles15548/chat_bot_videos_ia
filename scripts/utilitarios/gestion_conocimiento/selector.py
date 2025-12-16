import os
import json
import numpy as np
import faiss
from scripts.utilitarios.embedding.embedding import generar_embedding
from scripts.utilitarios.gestion_conocimiento.buscarPorNumero import capa_filtro_numero_video

DATA_DIR = "/opt/render/project/src/data"
INDEX_DIR = os.path.join(DATA_DIR, "indices")
METADATA_FILE = os.path.join(DATA_DIR, "metadata.json")

FAISS_INDEX = None
GLOBAL_METADATA = None
EMBED_MAP = []


def cargar_todos_los_indices():
    """Carga todos los embeddings (.npy) y su metadata."""

    global FAISS_INDEX, GLOBAL_METADATA, EMBED_MAP
    EMBED_MAP = []

    print("📥 Reconstruyendo FAISS global...")

    # Cargar metadata
    if not os.path.exists(METADATA_FILE):
        raise ValueError("⚠️ metadata.json no existe")
    with open(METADATA_FILE, "r", encoding="utf-8") as f:
        GLOBAL_METADATA = json.load(f)
    todos_embeddings = []


    archivos = [f for f in os.listdir(INDEX_DIR) if f.endswith(".npy")]
    archivos.sort()

    print("📂 Archivos encontrados en indices:", archivos)

    for archivo in archivos:
        ruta = os.path.join(INDEX_DIR, archivo)
        vid_id = archivo.replace(".npy","").replace(".index","")
        video_data = next((v for v in GLOBAL_METADATA["videos"] if v["num_video"] == vid_id), None)
        if not video_data:
            print(f"⚠️ WARNING: no hay metadata para {vid_id}, se ignora")
            continue
        
        emb = np.load(ruta)
        todos_embeddings.append(emb)

        for chunk_idx in range(emb.shape[0]):
            EMBED_MAP.append({
                "video":vid_id,
                "chunk": chunk_idx
            })
    # Unir todos los embeddings en un solo array
    if not todos_embeddings:
        raise ValueError("⚠️ No hay embeddings en indices/")

    matriz = np.vstack(todos_embeddings)
    print(f"📊 Total de embeddings cargados: {matriz.shape[0]}")
    dim = matriz.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(matriz)
    FAISS_INDEX = index
    print("✅ FAISS global listo")



def elegir_mejor_chunck(pregunta: str,ultimo_bot: str, cantidad_chunks: int):
    """Busca los chunks más relevantes desde FAISS + metadata.json"""
    global FAISS_INDEX, GLOBAL_METADATA, EMBED_MAP

    if FAISS_INDEX is None:
        cargar_todos_los_indices()

    # AQUI SE HARA LA CAPA FILTRO N° de video
    nueva_consulta_usuario = capa_filtro_numero_video(pregunta)
    # -- print de nueva consulta capa filtro
    print(nueva_consulta_usuario)
    
    consulta_extendida = f"Bod Dijo: {ultimo_bot}\n Usuario pregunta: {nueva_consulta_usuario}"

    
    # Crear embedding de la pregunta
    vec = np.array(generar_embedding(consulta_extendida), dtype=np.float32).reshape(1, -1)

    # Buscar globalmente
    distancias, ids = FAISS_INDEX.search(vec, cantidad_chunks)

    distancias = distancias.flatten()
    ids = ids.flatten()

    resultados = []

    for i, global_id in enumerate(ids):
        m = EMBED_MAP[global_id]  # video + chunk

        # Encontrar datos del video
        video_data = next(v for v in GLOBAL_METADATA["videos"] if v["num_video"] == m["video"])
        chunk_data = video_data["chunks"][m["chunk"]]

        resultados.append({
            "num_video": video_data["num_video"],
            "autor": video_data["autor"],
            "fecha": video_data["fecha"],
            "titulo": video_data["titulo"],
            "tags": video_data["tags"],
            "contenido": chunk_data["contenido"],
            "distancia": float(distancias[i]),
        })

    # Ordenar por relevancia
    resultados.sort(key=lambda x: x["distancia"])

    print("🎯 --- TOP CHUNKS ORDENADOS ---")
    for r in resultados:
        print(f"""
        🎬 Video: {r['num_video']}
        🎙️ Título: {r['titulo']}
        🧩 Texto: {r['contenido'][:150]}...
        """)


    return resultados
