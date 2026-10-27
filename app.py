import streamlit as st
from modelo.persistencia.db import inicializar_bd
from vista.paginas import inicio, configuracion, simulacion, reportes

st.set_page_config(page_title="Simulador Telecom", layout="wide")

# ⬅️ Se ejecuta una sola vez al arrancar
inicializar_bd()

PAGINAS = {
    "🏠 Inicio": inicio.render,
    "⚙️ Configuración": configuracion.render,
    "📊 Simulación": simulacion.render,
    "📈 Reportes": reportes.render,
}

with st.sidebar:
    st.title("Simulador de Atención")
    opcion = st.radio("Navegación", list(PAGINAS.keys()))

PAGINAS[opcion]()