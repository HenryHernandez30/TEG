"""Página de reportes y comparación de escenarios."""
import streamlit as st
import pandas as pd
import plotly.express as px
from modelo.persistencia.repositorio_resultados import RepositorioResultados
from modelo.colas.mmc import mmc_metricas


def render():
    st.header("📈 Reportes y validación")

    repo = RepositorioResultados()
    historial = repo.historial()

    if not historial:
        st.warning("Aún no hay simulaciones guardadas. Ejecuta alguna primero en **📊 Simulación**.")
        return

    # --- Tabla de historial ---
    st.subheader("Historial de simulaciones")
    df = pd.DataFrame(historial)
    st.dataframe(df, width="stretch")

    # --- Gráfica comparativa ---
    st.subheader("Comparación de escenarios")
    if len(df) > 1:
        fig = px.bar(
            df,
            x="escenario",
            y="espera_promedio",
            color="utilizacion",
            title="Tiempo de espera promedio por escenario",
            labels={"espera_promedio": "Wq (h)", "utilizacion": "Utilización"},
        )
        st.plotly_chart(fig, width="stretch")

    # --- Validación contra M/M/c ---
    st.subheader("🔍 Validación contra modelo analítico M/M/c")
    with st.expander("Ver fórmulas y comparación"):
        st.markdown("""
        El modelo analítico **M/M/c** asume:
        - Llegadas Poisson con tasa λ
        - Servicios exponenciales con tasa μ
        - c servidores en paralelo
        - Cola única, disciplina FIFO
        """)

        ultimo = df.iloc[0]
        analitico = mmc_metricas(
            ultimo["tasa_llegada"],
            ultimo["tasa_servicio"],
            int(ultimo["num_operadores"]),
        )
        st.write(f"Último escenario: **{ultimo['escenario']}**")
        st.write(f"- Wq simulado: `{ultimo['espera_promedio']:.4f}` h")
        st.write(
            f"- Utilización simulada: `{(ultimo['utilizacion'] or 0)*100:.2f}` %"
        )
        if not analitico["estable"]:
            st.write(
                f"- El modelo analítico no es estable (ρ = `{analitico['rho']:.2f}`)."
            )
        else:
            st.write(f"- Wq analítico: `{analitico['Wq']:.4f}` h")
            st.write(
                f"- Utilización analítica: `{analitico['rho']*100:.2f}` %"
            )