from sqlalchemy import create_engine, text
from dotenv import load_dotenv
load_dotenv()
import os
import numpy as np
import jwt,datetime,json


DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = "clave101"
ALGORITHM = "HS256"
# Crear engine
engine = create_engine(DATABASE_URL)


DATA_DIR ="/opt/render/proyect/src/data"
USER = os.path.join(DATA_DIR,"users.json")




# def listar_personas():
#     with engine.connect() as conn:
#         result = conn.execute(text("SELECT id, nombre, correo FROM persona"))
#         rows = result.fetchall()
#         print(rows)
#         return [{"id": r.id, "nombre": r.nombre,"correo": r.correo} for r in rows]



# def agrega(nombre, correo, contrasena):
#     with engine.connect() as conn:
#         query = text("""
#             INSERT INTO persona (nombre, correo, contrasena)
#             VALUES (:nombre, :correo, :contrasena1)
#             RETURNING id;
#         """)
#         result = conn.execute(query,{
#             "nombre": nombre,
#             "correo": correo,
#             "contrasena1": contrasena
#         })
#         persona_id = result.scalar()
        
#         conn.commit()
#         return persona_id


    



# def acceso(correo,contrasena):

#     with engine.connect() as conn:
#         query = text("""
#             SELECT id,contrasena,correo FROM persona
#             WHERE correo = :correo
#             LIMIT 1;
#         """)
#         result = conn.execute(query,{"correo":correo})
        
#         user = result.fetchone()
#         if user:
#                 if user.contrasena == contrasena:
#                     exp = datetime.datetime.utcnow() + datetime.timedelta(hours=3)
#                     token = jwt.encode(
#                         {"id": user.id, "correo": user.correo, "exp":exp},
#                         SECRET_KEY,
#                         algorithm=ALGORITHM
#                     )
#                     return {"id": user.id,"token":token, "message": "Ingresando"}
#                 else:
#                     return {"id":0, "message":"Contraseña incorrecta"}
            
#         else:
#             return {"id": 0, "message":"No se encontro usuario"}
 

def agregar(nombre, correo, contrasena,tipo):
    os.makedirs(DATA_DIR, exist_ok=True)

    # Leer si ya existe
    if os.path.exists(USER):
        
        with open(USER, "r", encoding="utf-8") as f:
            data = json.load(f)
        
    else:
        data = {"usuarios": []}

    nuevo_id = (max([u["id"] for u in data["usuarios"]] or [0]) + 1)
    nuevo_usuario = {
        "id": nuevo_id,
        "nombre": nombre,
        "correo": correo,
        "contrasena": contrasena,
        "tipo" : tipo
    }

    data["usuarios"].append(nuevo_usuario)

    with open(USER, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ Usuario '{nombre}' agregado correctamente.")
    return nuevo_usuario


# def acceso(correo,contrasena):

#     with engine.connect() as conn:
#         query = text("""
#             SELECT id,contrasena,correo FROM persona
#             WHERE correo = :correo
#             LIMIT 1;
#         """)
#         result = conn.execute(query,{"correo":correo})
        
#         user = result.fetchone()
#         if user:
#                 if user.contrasena == contrasena:
#                     exp = datetime.datetime.utcnow() + datetime.timedelta(hours=3)
#                     token = jwt.encode(
#                         {"id": user.id, "correo": user.correo, "exp":exp},
#                         SECRET_KEY,
#                         algorithm=ALGORITHM
#                     )
#                     return {"id": user.id,"token":token, "message": "Ingresando"}
#                 else:
#                     return {"id":0, "message":"Contraseña incorrecta"}
            
#         else:
#             return {"id": 0, "message":"No se encontro usuario"}

def acceso(correo,contrasena):

    if not os.path.exists(USER):
       return{"id":0, "message": "No hay usuarios registrados"}

    try:
        with open(USER,"r",encoding="utf-8") as f:
           data = json.load(f)
    except json.JSONDecodeError:
       return {"id":0, "message": "Archivo de usuario dañado"}

    user = next((u for u in data["usuarios"] if u["correo"] == correo),None)
    if not user:
        return {"id":0, "message":"No se encontró Usuario"}
    if user["contrasena"] != contrasena:
        return {"id":0, "message":"Contraseña incorrecta"}
    
    # Crear token JWT (igual que antes)
    exp = datetime.datetime.utcnow() + datetime.timedelta(hours=3)
    token = jwt.encode(
        {"id": user["id"], "correo": user["correo"], "exp": exp},
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    return {"id": user["id"], "tipo":user["tipo"] , "token":token, "message": "Ingresando"}
    




    