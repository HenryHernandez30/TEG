"""Pantalla de acceso SIMOP. Al entrar, la app abre Configuración."""
import re

import streamlit as st

from modelo.persistencia.repositorio_usuarios import RepositorioUsuarios

_USUARIO = re.compile(r"^[a-zA-Z0-9._@-]{3,}$")

PERFILES = {
    "Analista": "Crear y ejecutar escenarios de simulación.",
    "Supervisor": "Revisar resultados y aprobar propuestas.",
    "Administrador": "Gestionar usuarios, parámetros y datos.",
}

_PANEL = """
<section style="position:relative;overflow:hidden;min-height:78vh;border-radius:18px;color:#fff;background:#12284a url('/app/static/network.png') center/cover no-repeat;">
  <div style="position:absolute;inset:0;background:linear-gradient(to top,rgba(12,28,58,.94),rgba(12,28,58,.72) 48%,rgba(12,28,58,.28));"></div>
  <div style="position:relative;z-index:1;display:flex;flex-direction:column;justify-content:space-between;gap:28px;min-height:78vh;padding:36px 32px;box-sizing:border-box;">
    <div style="display:flex;align-items:center;gap:10px;">
      <span style="display:inline-flex;width:36px;height:36px;align-items:center;justify-content:center;border-radius:10px;background:#7ee0ea;color:#14304f;font-weight:700;">∿</span>
      <span>
        <span style="display:block;font-size:18px;font-weight:650;letter-spacing:-.02em;">SIMOP</span>
        <span style="display:block;margin-top:2px;font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:rgba(255,255,255,.65);">Simulador Telecom</span>
      </span>
    </div>
    <div>
      <p style="margin:0;font-size:12px;font-weight:600;letter-spacing:.14em;text-transform:uppercase;color:#8ef0e4;">Simulador computacional</p>
      <h2 style="margin:12px 0 0;font-size:30px;line-height:1.15;font-weight:600;">Optimización de la estructura operativa y los procesos de atención al cliente</h2>
      <p style="margin:10px 0 0;color:rgba(255,255,255,.72);">Empresa de telecomunicaciones</p>
      <ul style="margin:28px 0 0;padding:0;list-style:none;display:flex;flex-direction:column;gap:16px;">
        <li><strong>Procesos de atención al cliente.</strong> <span style="color:rgba(255,255,255,.72);">Modela colas, canales y tiempos de servicio.</span></li>
        <li><strong>Estructura operativa.</strong> <span style="color:rgba(255,255,255,.72);">Evalúa escenarios de personal, turnos y áreas.</span></li>
        <li><strong>Optimización basada en datos.</strong> <span style="color:rgba(255,255,255,.72);">Compara indicadores y elige la mejor configuración.</span></li>
      </ul>
      <dl style="margin:28px 0 0;display:grid;grid-template-columns:repeat(3,1fr);gap:12px;padding:16px;border-radius:14px;background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.12);">
        <div><dt style="font-size:12px;color:rgba(255,255,255,.62);">Tiempo medio de espera</dt><dd style="margin:4px 0 0;font-size:26px;color:#8ef0e4;">-38%</dd></div>
        <div><dt style="font-size:12px;color:rgba(255,255,255,.62);">Nivel de servicio</dt><dd style="margin:4px 0 0;font-size:26px;color:#8ef0e4;">92%</dd></div>
        <div><dt style="font-size:12px;color:rgba(255,255,255,.62);">Ocupación de agentes</dt><dd style="margin:4px 0 0;font-size:26px;color:#8ef0e4;">81%</dd></div>
      </dl>
      <p style="margin:8px 0 0;font-size:12px;color:rgba(255,255,255,.5);">Resultados de un escenario de ejemplo.</p>
    </div>
  </div>
</section>
"""


def render():
    if "login_rol" not in st.session_state:
        st.session_state["login_rol"] = "Analista"

    panel, acceso = st.columns([1.05, 0.95], vertical_alignment="center")
    with panel:
        st.html(_PANEL)

    with acceso:
        st.badge("Acceso restringido", color="gray", icon=":material/lock:")
        st.title("Iniciar sesión")
        st.caption(
            "Accede al simulador para modelar escenarios y optimizar "
            "la operación y la atención al cliente."
        )

        rol = st.segmented_control(
            "Perfil de acceso",
            list(PERFILES),
            key="login_rol",
            required=True,
            width="stretch",
            wrap=True,
        )
        st.caption(PERFILES.get(rol, ""))

        with st.form("acceso_simop", border=False):
            usuario = st.text_input(
                "Usuario o correo institucional",
                placeholder="jperez o jperez@empresa.com",
            )
            clave = st.text_input(
                "Contraseña",
                type="password",
                placeholder="••••••••",
            )
            st.checkbox("Recordar este equipo")
            entrar = st.form_submit_button(
                "Ingresar al simulador",
                type="primary",
                width="stretch",
                icon=":material/login:",
            )

        if entrar:
            error = _validar(usuario, clave, rol)
            if error:
                st.error(error)
            else:
                cuenta = RepositorioUsuarios().autenticar(usuario, clave)
                if cuenta is None:
                    st.error("Usuario o contraseña incorrectos.")
                elif cuenta["rol"] != rol:
                    st.error("Este usuario no corresponde al perfil seleccionado.")
                else:
                    st.session_state["usuario"] = cuenta
                    st.session_state.pop("nav", None)
                    st.rerun()

        st.caption(
            "Cuentas de demostración: analista, supervisor y admin. "
            "Contraseña: Simop2026."
        )
        st.caption("¿No tienes acceso? Solicítalo al administrador del sistema.")
        st.caption("© 2026 SIMOP · Simulador de operaciones Telecom")


def _validar(usuario: str, clave: str, rol: str | None) -> str | None:
    usuario = (usuario or "").strip()
    if not rol:
        return "Elige un perfil de acceso."
    if not usuario:
        return "Ingresa tu usuario o correo institucional."
    if not _USUARIO.match(usuario):
        return "El usuario no tiene un formato válido."
    if not clave:
        return "Ingresa tu contraseña."
    if len(clave) < 8:
        return "La contraseña debe tener al menos 8 caracteres."
    return None
