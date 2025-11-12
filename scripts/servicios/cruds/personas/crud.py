from sqlalchemy import create_engine, text
from dotenv import load_dotenv
load_dotenv()
import os
import numpy as np
import jwt,datetime


DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = "clave101"
ALGORITHM = "HS256"
# Crear engine
engine = create_engine(DATABASE_URL)


def listar_personas():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT id, nombre, correo FROM persona"))
        rows = result.fetchall()
        print(rows)
        return [{"id": r.id, "nombre": r.nombre,"correo": r.correo} for r in rows]


def eliminar(id: int):
    with engine.connect() as conn:
        result = conn.execute(text("DELETE FROM persona WHERE id = :id RETURNING id"), {"id": id})
        conn.commit()
        deleted = result.fetchone()
        if deleted:
            print(f"🗑️ Persona con ID {id} eliminada correctamente.")
        else:
            print(f"⚠️ No se encontró ninguna Archivo con ID {id}.")


def agregar(nombre, correo, contrasena):
    with engine.connect() as conn:
        query = text("""
            INSERT INTO persona (nombre, correo, contrasena)
            VALUES (:nombre, :correo, :contrasena1)
            RETURNING id;
        """)
        result = conn.execute(query,{
            "nombre": nombre,
            "correo": correo,
            "contrasena1": contrasena
        })
        persona_id = result.scalar()
        
        conn.commit()
        return persona_id




def acceso(correo,contrasena):

    with engine.connect() as conn:
        query = text("""
            SELECT id,contrasena1,correo FROM persona
            WHERE correo = :correo
            LIMIT 1;
        """)
        result = conn.execute(query,{"correo":correo})
        
        user = result.fetchone()
        if user:
                if user.contrasena == contrasena:
                    exp = datetime.datetime.utcnow() + datetime.timedelta(hours=3)
                    token = jwt.encode(
                        {"id": user.id, "correo": user.correo, "exp":exp},
                        SECRET_KEY,
                        algorithm=ALGORITHM
                    )
                    return {"id": user.id,"token":token, "message": "Ingresando"}
                else:
                    return {"id":0, "message":"Contraseña incorrecta"}
            
        else:
            return {"id": 0, "message":"No se encontro usuario"}
 


from datetime import date
if __name__ == "__main__":
     
    # agregar(
    # nombre="Jose",
    # apellidos=" Jaimes Soto",
    # fecha_nacimiento=None,
    # correo="jose@example.com",
    # contrasena1="12345",
    # contrasena2="12345"
    # )
    
    

    # editar(
    # id = 1,
    # nombre="Charles",
    # apellidos="Huamán Llacta",
    # fecha_nacimiento=date(2000, 5, 10),
    # correo="charles@example.com",
    # contrasena1="12345",
    # contrasena2="12345"
    # )

     
    #eliminar(5)
    listar_personas()