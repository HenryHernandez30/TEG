"""Página de inicio del simulador."""
import streamlit as st


def render():
    st.title("🎯 Simulador de Atención al Cliente")
    st.subheader("Empresa de Telecomunicaciones")

    st.markdown("""
    ### Descripción del proyecto

    Herramienta computacional basada en **Simulación de Eventos Discretos (DES)**
    para optimizar la estructura operativa y los procesos de atención al cliente
    en una empresa de telecomunicaciones.

    ### ¿Qué puedes hacer aquí?

    - **⚙️ Configuración:** define parámetros del sistema (operadores, tasas de llegada/servicio, horizonte)
    - **📊 Simulación:** ejecuta el modelo M/M/c y visualiza métricas clave
    - **📈 Reportes:** compara escenarios y valida contra el modelo analítico

    ### Objetivos específicos cubiertos

    1. **Diagnóstico:** análisis del flujo de atención actual
    2. **Diseño:** arquitectura conceptual del simulador y modelo de colas
    3. **Programación:** motor de simulación de eventos discretos
    4. **Validación:** comparación con el modelo analítico M/M/c
    """)

    st.info("👈 Comienza por la página **⚙️ Configuración** en el menú lateral.")