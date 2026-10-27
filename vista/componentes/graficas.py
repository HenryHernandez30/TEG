"""Componentes de gráficas reutilizables."""
import streamlit as st
import plotly.graph_objects as go


def grafica_metricas(resultado: dict):
    """Muestra métricas clave en tarjetas y una gráfica resumen."""
    st.subheader("📊 Métricas de la simulación")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Clientes atendidos", resultado["clientes_atendidos"])
    c2.metric("Wq promedio", f"{resultado['espera_promedio']:.3f} h")
    c3.metric("Utilización", f"{resultado['utilizacion_operadores']*100:.1f} %")
    c4.metric("Throughput", f"{resultado['throughput']:.2f}/h")

    # Gráfica de barras con las métricas clave
    metricas = {
        "Clientes atendidos": resultado["clientes_atendidos"],
        "Throughput (x10)": resultado["throughput"] * 10,
        "Utilización (%)": resultado["utilizacion_operadores"] * 100,
        "Wq (horas x10)": resultado["espera_promedio"] * 10,
    }
    fig = go.Figure(data=[
        go.Bar(x=list(metricas.keys()), y=list(metricas.values()),
               marker_color=["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"])
    ])
    fig.update_layout(title="Resumen de métricas",
                      yaxis_title="Valor (normalizado)",
                      showlegend=False)
    st.plotly_chart(fig, width="stretch")


def grafica_distribucion_esperas(tickets):
    """Histograma de tiempos de espera."""
    import plotly.express as px
    esperas = [t.tiempo_espera for t in tickets if t]
    if not esperas:
        st.info("Sin datos de espera para graficar.")
        return
    fig = px.histogram(x=esperas, nbins=30,
                       title="Distribución de tiempos de espera",
                       labels={"x": "Tiempo de espera (h)", "y": "Frecuencia"})
    st.plotly_chart(fig, width="stretch")