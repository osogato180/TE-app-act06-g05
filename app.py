import database as db
import streamlit as st

st.set_page_config(page_title="Gestión de Citas Médicas", layout="wide")
st.title("🏥 Sistema de Gestión de Citas Médicas (MongoDB Atlas)")

# Menú de navegación CRUD
menu = ["Registrar Cita", "Consultar Citas", "Actualizar Cita", "Eliminar Cita"]
opcion = st.sidebar.selectbox("Seleccione una operación", menu)

# 1. REGISTRAR
if opcion == "Registrar Cita":
  st.subheader("📝 Registrar Nueva Cita")
  with st.form("form_registro"):
    paciente = st.text_input("Nombre Completo del Paciente")
    especialidad = st.selectbox(
        "Especialidad",
        ["Medicina General", "Pediatría", "Ginecología", "Cardiología"],
    )
    medico = st.text_input("Médico Asignado")
    fecha_cita = st.date_input("Fecha de la Cita")
    btn_guardar = st.form_submit_button("Guardar en MongoDB Atlas")

    if btn_guardar:
      if paciente and medico:
        db.registrar_cita(paciente, especialidad, medico, fecha_cita)
        st.success(f"Cita registrada con éxito para {paciente}.")
      else:
        st.error("Por favor complete todos los campos obligatorios.")

# 2. CONSULTAR
elif opcion == "Consultar Citas":
  st.subheader("🔍 Citas Registradas")
  if st.button("Refrescar Datos"):
    st.rerun()

  citas = db.obtener_todas_las_citas()
  if citas:
    for c in citas:
      with st.expander(f"📌 Paciente: {c.get('paciente')} - {c.get('fecha_cita')}"):
        st.write(f"**Especialidad:** {c.get('especialidad')}")
        st.write(f"**Médico:** {c.get('medico')}")
        st.write(f"**Estado:** {c.get('estado')}")
        st.caption(f"ID MongoDB: {c['_id']}")
  else:
    st.info("No hay citas registradas en la base de datos.")

# 3. ACTUALIZAR
elif opcion == "Actualizar Cita":
  st.subheader("🔄 Actualizar Cita")
  citas = db.obtener_todas_las_citas()
  if citas:
    dict_citas = {
        f"{c['paciente']} | {c['especialidad']} ({c['fecha_cita']})": c
        for c in citas
    }
    seleccion = st.selectbox(
        "Seleccione la cita a modificar", list(dict_citas.keys())
    )
    cita_obj = dict_citas[seleccion]

    nuevo_estado = st.selectbox(
        "Estado",
        ["Programada", "Atendida", "Cancelada"],
        index=["Programada", "Atendida", "Cancelada"].index(
            cita_obj.get("estado", "Programada")
        ),
    )
    nuevo_medico = st.text_input(
        "Médico Asignado", value=cita_obj.get("medico", "")
    )

    if st.button("Actualizar Registro"):
      db.actualizar_cita(cita_obj["_id"], nuevo_estado, nuevo_medico)
      st.success("¡Registro actualizado exitosamente!")
      st.rerun()
  else:
    st.info("No hay datos para actualizar.")

# 4. ELIMINAR
elif opcion == "Eliminar Cita":
  st.subheader("🗑️ Eliminar Cita")
  citas = db.obtener_todas_las_citas()
  if citas:
    dict_citas = {
        f"{c['paciente']} | {c['especialidad']} ({c['fecha_cita']})": c["_id"]
        for c in citas
    }
    seleccion = st.selectbox(
        "Seleccione la cita a eliminar", list(dict_citas.keys())
    )

    if st.button("Eliminar Definitivamente", type="primary"):
      db.eliminar_cita(dict_citas[seleccion])
      st.success("Cita eliminada de MongoDB Atlas.")
      st.rerun()
  else:
    st.info("No hay datos para eliminar.")
