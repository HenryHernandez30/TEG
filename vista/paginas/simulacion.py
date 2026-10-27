import streamlit as st
import pandas as pd
from controlador.controlador_simulacion import ControladorSimulacion
from vista.componentes.fila import render_fila
from vista.componentes.graficas import grafica_metricas


@st.fragment
def _detalle_numerico():
    resultado = st.session_state.get("resultado")
    ctrl = st.session_state.get("controlador")
    if not resultado:
        return
    with st.expander("Detalle numérico"):
        grafica_metricas(resultado)
        if ctrl is not None:
            comp = ctrl.comparar_con_analitico()
            if comp:
                st.subheader("Validación vs M/M/c analítico")
                st.dataframe(pd.DataFrame([comp]), width="stretch")


def render():
    st.header("Atención al cliente")
    st.caption("Los clientes entran, hacen fila y pasan al primer mostrador libre.")

    config = st.session_state.get("config")
    if not config:
        st.warning("Primero configura los parámetros.")
        return

    if st.button("Ejecutar simulación", type="primary"):
        ctrl = ControladorSimulacion()
        escenario_id = config.get("escenario_id")
        with st.spinner("Simulando..."):
            resultado = ctrl.ejecutar(config, escenario_id=escenario_id)
        st.session_state["resultado"] = resultado
        st.session_state["controlador"] = ctrl
        st.session_state["trazas"] = ctrl.trazas
        st.session_state["corrida"] = st.session_state.get("corrida", 0) + 1
        if escenario_id:
            st.success("Resultado guardado en el historial.")

    render_fila(
        st.session_state.get("trazas"),
        int(config["num_operadores"]),
        int(st.session_state.get("corrida", 0)),
    )

    resultado = st.session_state.get("resultado")
    if resultado:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Atendidos", resultado["clientes_atendidos"])
        c2.metric("Espera promedio", f"{resultado['espera_promedio']:.2f} h")
        c3.metric("Utilización", f"{resultado['utilizacion_operadores']*100:.1f}%")
        c4.metric("Throughput", f"{resultado['throughput']:.2f}/h")
        _detalle_numerico()
