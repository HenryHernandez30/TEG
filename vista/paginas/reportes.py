"""Página de reportes y comparación de escenarios."""
from datetime import date, datetime

import streamlit as st
import pandas as pd
import plotly.express as px
from modelo.persistencia.repositorio_resultados import RepositorioResultados
from modelo.colas.mmc import mmc_metricas


def _dia(fila: dict) -> date | None:
    texto = str(fila.get("ejecutado_en") or "")[:10]
    try:
        return datetime.strptime(texto, "%Y-%m-%d").date()
    except ValueError:
        return None


def _etiqueta(fila: dict) -> str:
    cuando = fila.get("ejecutado_en") or "sin fecha"
    return f"#{fila['id']} · {fila['escenario']} · {cuando}"


@st.dialog("Borrar reportes")
def _confirmar_borrado(mensaje: str, ids: list[int] | None = None, todo: bool = False, antes_de: str | None = None):
    st.warning(mensaje)
    if st.button("Borrar", type="primary", icon=":material/delete:"):
        repo = RepositorioResultados()
        if todo:
            cantidad = repo.eliminar_todos()
        elif antes_de:
            cantidad = repo.eliminar_anteriores(antes_de)
        else:
            cantidad = repo.eliminar_ids(ids or [])
        st.session_state["aviso_borrado"] = cantidad
        st.rerun()


def _limpiar(historial: list[dict]):
    st.subheader("Limpiar reportes")
    st.caption(
        "Quita simulaciones guardadas cuando lo necesites. "
        "Los escenarios de configuración se conservan."
    )

    etiquetas = {_etiqueta(fila): int(fila["id"]) for fila in historial}
    elegidos = st.multiselect(
        "Reportes a borrar",
        list(etiquetas),
        placeholder="Elige uno o más",
    )
    if st.button(
        "Borrar seleccionados",
        icon=":material/delete:",
        disabled=not elegidos,
    ):
        cantidad = len(elegidos)
        texto = "1 reporte seleccionado" if cantidad == 1 else f"{cantidad} reportes seleccionados"
        _confirmar_borrado(
            f"Se borrará {texto}." if cantidad == 1 else f"Se borrarán {texto}.",
            ids=[etiquetas[nombre] for nombre in elegidos],
        )

    fecha = st.date_input(
        "Borrar reportes anteriores a",
        value=date.today(),
        key="fecha_limpieza",
    )
    antiguos = [
        fila for fila in historial
        if (dia := _dia(fila)) is not None and dia < fecha
    ]
    if st.button(
        "Borrar anteriores a esa fecha",
        icon=":material/history:",
        disabled=not antiguos,
    ):
        cantidad = len(antiguos)
        texto = "1 reporte" if cantidad == 1 else f"{cantidad} reportes"
        _confirmar_borrado(
            f"Se borrará {texto} anterior al {fecha.strftime('%d/%m/%Y')}."
            if cantidad == 1
            else f"Se borrarán {texto} anteriores al {fecha.strftime('%d/%m/%Y')}.",
            antes_de=fecha.isoformat(),
        )

    if st.button("Borrar todo el historial", icon=":material/delete_sweep:"):
        _confirmar_borrado(
            f"Se borrarán las {len(historial)} simulaciones guardadas." if len(historial) != 1 else "Se borrará la simulación guardada.",
            todo=True,
        )


def render():
    st.header("Reportes y validación")

    aviso = st.session_state.pop("aviso_borrado", None)
    if aviso is not None:
        st.success(f"Se borraron {aviso} reportes.")

    repo = RepositorioResultados()
    historial = repo.historial()

    if not historial:
        st.warning("Aún no hay simulaciones guardadas. Ejecuta alguna primero en Simulación.")
        return

    _limpiar(historial)

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