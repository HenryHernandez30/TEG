import streamlit as st
from modelo.persistencia.db import inicializar_bd
from vista.paginas import configuracion, login, reportes, simulacion

st.set_page_config(
    page_title="SIMOP · Simulador Telecom",
    layout="wide",
    initial_sidebar_state="expanded",
)

inicializar_bd()

if not st.session_state.get("usuario"):
    login.render()
    st.stop()

st.session_state.pop("login_clave", None)

PAGINAS = {
    "Configuración": configuracion.render,
    "Simulación": simulacion.render,
    "Reportes": reportes.render,
}

if "nav" not in st.session_state:
    st.session_state["nav"] = "Configuración"

usuario = st.session_state["usuario"]
with st.sidebar:
    st.markdown("**SIMOP**")
    st.caption("Simulador Telecom")
    st.write(usuario["nombre"])
    st.caption(usuario["rol"])
    if st.button("Cerrar sesión", width="stretch", icon=":material/logout:"):
        for clave in ("usuario", "nav", "login_usuario", "login_clave"):
            st.session_state.pop(clave, None)
        st.rerun()
    opcion = st.radio("Navegación", list(PAGINAS), key="nav")

PAGINAS[opcion]()
