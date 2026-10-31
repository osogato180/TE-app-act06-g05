from datetime import datetime
import database as db
import streamlit as st

st.set_page_config(
    page_title="Gestión de Citas Médicas", layout="wide"
)
st.title("🏥 Sistema de Gestión de Citas Médicas (MongoDB Atlas)")

# Diccionario con especialidades y exactamente 3 médicos ÚNICOS por cada campo
ESPECIALIDADES_MEDICOS = {
    "Medicina General": [
        "Dr. Carlos Pérez",
        "Dra. Ana Gómez",
        "Dr. Luis Torres",
    ],
    "Pediatría": [
        "Dra. María Fernández",
        "Dr. Jorge Ramírez",
        "Dra. Sofía Castro",
    ],
    "Ginecología": [
        "Dra. Carmen Ruiz",
        "Dr. Javier Morales",
        "Dra. Elena Vargas",
    ],
    "Cardiología": [
        "Dr. Roberto Silva",
        "Dra. Patricia Rojas",
        "Dr. Fernando Paredes",
    ],
    "Dermatología": [
        "Dra. Lucía Mendoza",
        "Dr. Ricardo Castillo",
        "Dra. Andrea Benites",
    ],
    "Oftalmología": [
        "Dr. Gabriel Herrera",
        "Dra. Claudia Espinoza",
        "Dr. Hugo Paredes",
    ],
}

# Menú de navegación CRUD
menu = [
    "Registrar Cita",
    "Consultar Citas",
    "Actualizar Cita",
    "Eliminar Cita",
]
opcion = st.sidebar.selectbox("Seleccione una operación", menu)

# 1. REGISTRAR
if opcion == "Registrar Cita":
  st.subheader("📝 Registrar Nueva Cita")
  with st.form("form_registro"):
    paciente = st.text_input("Nombre Completo del Paciente")

    especialidad = st.selectbox(
        "Especialidad", list(ESPECIALIDADES_MEDICOS.keys()), key="reg_especialidad"
    )

    # Los médicos se actualizan dinámicamente según la especialidad seleccionada
    medicos_disponibles = ESPECIALIDADES_MEDICOS[especialidad]
    medico = st.selectbox(
        "Médico Asignado", medicos_disponibles, key="reg_medico"
    )

    fecha_cita = st.date_input("Fecha de la Cita")
    btn_guardar = st.form_submit_button("Guardar en MongoDB Atlas")

    if btn_guardar:
      if paciente:
        db.registrar_cita(paciente, especialidad, medico, fecha_cita)
        st.success(
            f"Cita registrada con éxito para {paciente} con el/la {medico}"
            f" ({especialidad})."
        )
      else:
        st.error("Por favor ingrese el nombre del paciente.")

# 2. CONSULTAR
elif opcion == "Consultar Citas":
  st.subheader("🔍 Citas Registradas")
  if st.button("Refrescar Datos"):
    st.rerun()

  citas = db.obtener_todas_las_citas()
  if citas:
    for c in citas:
      with st.expander(
          f"📌 Paciente: {c.get('paciente')} - {c.get('especialidad')} ({c.get('fecha_cita')})"
      ):
        st.write(f"**Especialidad:** {c.get('especialidad')}")
        st.write(f"**Médico Asignado:** {c.get('medico')}")
        st.write(f"**Estado:** {c.get('estado')}")
        st.caption(f"ID MongoDB: {c['_id']}")
  else:
    st.info("No hay citas registradas en la base de datos.")

# 3. ACTUALIZAR (Con búsqueda específica y cambio dinámico de médicos)
elif opcion == "Actualizar Cita":
  st.subheader("🔄 Buscar y Actualizar Cita")
  citas = db.obtener_todas_las_citas()

  if citas:
    # Buscador para filtrar al paciente en específico rápidamente
    busqueda = st.text_input(
        "🔍 Buscar paciente por nombre para modificar:"
    )

    citas_filtradas = [
        c
        for c in citas
        if busqueda.lower() in c.get("paciente", "").lower()
    ]

    if not citas_filtradas and busqueda:
      st.warning("No se encontraron pacientes con ese nombre.")
    else:
      lista_a_mostrar = citas_filtradas if busqueda else citas

      dict_citas = {
          f"{c['paciente']} | {c['especialidad']} - {c['fecha_cita']}": c
          for c in lista_a_mostrar
      }
      seleccion = st.selectbox(
          "Seleccione la cita exacta a modificar", list(dict_citas.keys())
      )
      cita_obj = dict_citas[seleccion]

      st.markdown("---")
      st.write(f"**Modificando a:** {cita_obj['paciente']}")

      # Modificar Estado
      nuevo_estado = st.selectbox(
          "Nuevo Estado",
          ["Programada", "Atendida", "Cancelada"],
          index=["Programada", "Atendida", "Cancelada"].index(
              cita_obj.get("estado", "Programada")
          ),
      )

      # Modificar Especialidad
      esp_actual = cita_obj.get(
          "especialidad", list(ESPECIALIDADES_MEDICOS.keys())[0]
      )
      idx_esp = (
          list(ESPECIALIDADES_MEDICOS.keys()).index(esp_actual)
          if esp_actual in ESPECIALIDADES_MEDICOS
          else 0
      )

      nueva_especialidad = st.selectbox(
          "Nueva Especialidad",
          list(ESPECIALIDADES_MEDICOS.keys()),
          index=idx_esp,
          key="select_nueva_esp",
      )

      # Actualiza automáticamente los 3 médicos exclusivos de la nueva especialidad seleccionada
      medicos_disponibles_actualizacion = ESPECIALIDADES_MEDICOS[
          nueva_especialidad
      ]
      med_actual = cita_obj.get("medico", medicos_disponibles_actualizacion[0])
      idx_med = (
          medicos_disponibles_actualizacion.index(med_actual)
          if med_actual in medicos_disponibles_actualizacion
          else 0
      )

      nuevo_medico = st.selectbox(
          "Nuevo Médico Asignado",
          medicos_disponibles_actualizacion,
          index=idx_med,
          key="select_nuevo_med",
      )

      # Modificar Fecha
      try:
        fecha_default = datetime.strptime(
            cita_obj.get("fecha_cita"), "%Y-%m-%d"
        ).date()
      except:
        fecha_default = datetime.today().date()

      nueva_fecha = st.date_input("Nueva Fecha de Cita", value=fecha_default)

      if st.button("Guardar Cambios en MongoDB"):
        db.actualizar_cita(
            cita_obj["_id"],
            nuevo_estado,
            nueva_especialidad,
            nuevo_medico,
            nueva_fecha,
        )
        st.success("¡Cita actualizada exitosamente en la nube!")
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
