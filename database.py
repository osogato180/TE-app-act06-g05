from datetime import datetime
import pymongo
import streamlit as st


@st.cache_resource
def get_database():
  """Establece la conexión con el clúster de MongoDB Atlas."""
  # La URI se recupera de forma segura desde los secrets de Streamlit o variable local
  mongo_uri = st.secrets["MONGO_URI"]
  client = pymongo.MongoClient(mongo_uri)
  return client["citas_medicas_db"]


def obtener_coleccion():
  db = get_database()
  return db["citas"]


# --- OPERACIÓN: REGISTRAR (CREATE) ---
def registrar_cita(paciente, especialidad, medico, fecha_cita):
  coleccion = obtener_coleccion()
  nueva_cita = {
      "paciente": paciente,
      "especialidad": especialidad,
      "medico": medico,
      "fecha_cita": str(fecha_cita),
      "estado": "Programada",
      "fecha_registro": datetime.now(),
  }
  return coleccion.insert_one(nueva_cita)


# --- OPERACIÓN: CONSULTAR (READ) ---
def obtener_todas_las_citas():
  coleccion = obtener_coleccion()
  return list(coleccion.find())


# --- OPERACIÓN: ACTUALIZAR (UPDATE) ---
def actualizar_cita(id_cita, nuevo_estado, nuevo_medico):
  coleccion = obtener_coleccion()
  return coleccion.update_one(
      {"_id": id_cita},
      {"$set": {"estado": nuevo_estado, "medico": nuevo_medico}},
  )


# --- OPERACIÓN: ELIMINAR (DELETE) ---
def eliminar_cita(id_cita):
  coleccion = obtener_coleccion()
  return coleccion.delete_one({"_id": id_cita})
