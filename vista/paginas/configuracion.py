import streamlit as st
from modelo.persistencia.repositorio_escenarios import (
    RepositorioEscenarios, Escenario
)

def _asignar_campos(nombre, operadores, llegada, servicio, horizonte):
    st.session_state["cfg_nombre"] = nombre
    st.session_state["cfg_n"] = int(operadores)
    st.session_state["cfg_lam"] = float(llegada)
    st.session_state["cfg_mu"] = float(servicio)
    st.session_state["cfg_T"] = float(horizonte)


def render():
    st.header("⚙️ Configuración")

    repo = RepositorioEscenarios()

    # --- Cargar escenario guardado ---
    escenarios = repo.listar()
    opciones = {}
    sel = "<Nuevo>"
    if escenarios:
        opciones = {f"{e.nombre} (ID {e.id})": e for e in escenarios}
        sel = st.selectbox(
            "Cargar escenario guardado",
            ["<Nuevo>"] + list(opciones.keys()),
        )

    if "cfg_nombre" not in st.session_state:
        _asignar_campos("Escenario base", 5, 40.0, 12.0, 24.0)

    if sel != st.session_state.get("_escenario_sel"):
        st.session_state["_escenario_sel"] = sel
        if sel == "<Nuevo>":
            _asignar_campos("Escenario base", 5, 40.0, 12.0, 24.0)
        else:
            e = opciones[sel]
            _asignar_campos(
                e.nombre, e.num_operadores,
                e.tasa_llegada, e.tasa_servicio, e.horizonte,
            )

    if sel != "<Nuevo>":
        e = opciones[sel]
        st.session_state["config"] = {
            "num_operadores": e.num_operadores,
            "tasa_llegada": e.tasa_llegada,
            "tasa_servicio": e.tasa_servicio,
            "tiempo_simulacion": e.horizonte,
            "escenario_id": e.id,
        }

    # --- Formulario ---
    with st.form("form_config"):
        nombre = st.text_input("Nombre del escenario", key="cfg_nombre")
        col1, col2 = st.columns(2)
        with col1:
            n = st.slider("Nº operadores", 1, 30, key="cfg_n")
            lam = st.number_input("λ (tickets/h)", 0.1, 200.0, key="cfg_lam")
        with col2:
            mu = st.number_input("μ (tickets/h)", 0.1, 100.0, key="cfg_mu")
            T = st.number_input("Horizonte (h)", 1.0, 720.0, key="cfg_T")

        if st.form_submit_button("💾 Guardar escenario"):
            esc_id = repo.guardar(Escenario(
                nombre=nombre, num_operadores=n,
                tasa_llegada=lam, tasa_servicio=mu,
                horizonte=T,
            ))
            st.session_state["config"] = {
                "num_operadores": n, "tasa_llegada": lam,
                "tasa_servicio": mu, "tiempo_simulacion": T,
                "escenario_id": esc_id,
            }
            st.success(f"✅ Escenario '{nombre}' guardado (ID {esc_id})")