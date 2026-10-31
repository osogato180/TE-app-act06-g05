from datetime import datetime
import pymongo
import streamlit as st


@st.cache_resource
def get_database():
  """Establece la conexión con el clúster de MongoDB Atlas."""
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


# --- OPERACIÓN: ACTUALIZAR (UPDATE - Modificado para permitir cambiar especialidad y médico) ---
def actualizar_cita(
    id_cita, nuevo_estado, nueva_especialidad, nuevo_medico, nueva_fecha
):
  coleccion = obtener_coleccion()
  return coleccion.update_one(
      {"_id": id_cita},
      {
          "$set": {
              "estado": nuevo_estado,
              "especialidad": nueva_especialidad,
              "medico": nuevo_medico,
              "fecha_cita": str(nueva_fecha),
          }
      },
  )


# --- OPERACIÓN: ELIMINAR (DELETE) ---
def eliminar_cita(id_cita):
  coleccion = obtener_coleccion()
  return coleccion.delete_one({"_id": id_cita})
