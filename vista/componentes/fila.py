"""Escena mínima de la fila: clientes y mostradores, cuadro a cuadro."""
import streamlit as st

LIMITE_CUADROS = 420

_HTML = """
<div class="escena">
  <div class="barra">
    <span class="marca">Atención al cliente</span>
    <span id="reloj">00:00</span>
  </div>
  <div class="sala">
    <section class="zona">
      <span class="etiqueta">Entrada y fila</span>
      <div id="fila" class="personas"></div>
    </section>
    <section class="zona">
      <span class="etiqueta">Mostradores</span>
      <div id="mostradores" class="escritorios"></div>
    </section>
  </div>
  <p id="detalle"></p>
  <div class="controles">
    <button id="play" type="button">Pausa</button>
    <button id="x1" type="button" class="vel" data-vel="1">1×</button>
    <button id="x2" type="button" class="vel" data-vel="2">2×</button>
    <button id="x4" type="button" class="vel" data-vel="4">4×</button>
    <span id="paso"></span>
  </div>
</div>
"""

_CSS = """
.escena {
  box-sizing: border-box;
  min-height: 320px;
  padding: 16px 18px 14px;
  color: var(--st-text-color, #fafafa);
  background: var(--st-secondary-background-color, #16181d);
  border: 1px solid var(--st-border-color, rgba(255, 255, 255, 0.12));
  border-radius: var(--st-base-radius, 12px);
  font-family: var(--st-font, sans-serif);
}
.barra, .controles {
  display: flex;
  align-items: center;
  gap: 8px;
}
.barra { justify-content: space-between; }
.marca {
  font-size: 13px;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  opacity: 0.72;
}
#reloj {
  font-variant-numeric: tabular-nums;
  font-size: 20px;
  font-weight: 600;
}
.sala {
  display: flex;
  flex-direction: column;
  gap: 18px;
  margin: 16px 0 8px;
}
.zona { min-width: 0; }
.etiqueta {
  display: block;
  margin-bottom: 10px;
  font-size: 12px;
  opacity: 0.6;
}
.personas, .escritorios {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  gap: 8px;
  min-height: 78px;
}
.vacio {
  align-self: center;
  font-size: 13px;
  opacity: 0.55;
}
.persona {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 34px;
  gap: 2px;
}
.cabeza, .cuerpo { background: var(--c, #7eb6ff); }
.cabeza {
  width: 14px;
  height: 14px;
  border-radius: 50%;
}
.cuerpo {
  width: 20px;
  height: 13px;
  border-radius: 9px 9px 6px 6px;
}
.num {
  font-size: 10px;
  line-height: 1;
  opacity: 0.65;
}
.persona.activa .cabeza {
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--c, #7eb6ff) 45%, transparent);
}
.extra {
  display: grid;
  place-items: center;
  width: 28px;
  height: 28px;
  margin-bottom: 14px;
  border-radius: 50%;
  font-size: 11px;
  border: 1px solid var(--st-border-color, rgba(255, 255, 255, 0.2));
}
.escritorio {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 58px;
  gap: 6px;
}
.hueco {
  width: 14px;
  height: 14px;
  margin-top: 2px;
  border-radius: 50%;
  border: 1.5px dashed var(--st-border-color, rgba(255, 255, 255, 0.35));
  opacity: 0.8;
}
.mesa {
  width: 46px;
  height: 7px;
  border-radius: 4px;
  background: var(--st-primary-color, #ff4b4b);
}
.puesto {
  font-size: 11px;
  opacity: 0.6;
}
#detalle {
  min-height: 1.3em;
  margin: 8px 0 12px;
  font-size: 15px;
}
.controles { flex-wrap: wrap; }
button {
  margin: 0;
  padding: 4px 12px;
  color: inherit;
  font: inherit;
  font-size: 13px;
  background: transparent;
  border: 1px solid var(--st-border-color, rgba(255, 255, 255, 0.2));
  border-radius: 999px;
  cursor: pointer;
}
button.activo {
  color: var(--st-background-color, #111);
  background: var(--st-primary-color, #ff4b4b);
  border-color: transparent;
}
#paso {
  margin-left: auto;
  font-size: 12px;
  opacity: 0.55;
}
"""

_JS = """
const COLORES = ["#7eb6ff", "#f0a36b", "#7dcea0", "#e7a0a4", "#c9a6e0", "#e6c86e", "#7ed0c4", "#f0b4ae"];

function reloj(horas) {
  const h = Math.floor(horas);
  const m = Math.floor((horas - h) * 60);
  return String(h).padStart(2, "0") + ":" + String(m).padStart(2, "0");
}

function persona(id, activa) {
  const el = document.createElement("div");
  el.className = activa ? "persona activa" : "persona";
  el.style.setProperty("--c", COLORES[Math.abs(id) % COLORES.length]);
  el.title = "Cliente " + id;
  const cabeza = document.createElement("span");
  cabeza.className = "cabeza";
  const cuerpo = document.createElement("span");
  cuerpo.className = "cuerpo";
  const num = document.createElement("span");
  num.className = "num";
  num.textContent = String(id);
  el.append(cabeza, cuerpo, num);
  return el;
}

function pintar(root, frame, total, index) {
  const fila = root.querySelector("#fila");
  const desks = root.querySelector("#mostradores");
  fila.replaceChildren();
  desks.replaceChildren();

  const cola = (frame && frame.cola) || [];
  if (!cola.length) {
    const vacio = document.createElement("span");
    vacio.className = "vacio";
    vacio.textContent = "Nadie en espera";
    fila.append(vacio);
  } else {
    cola.forEach((id) => fila.append(persona(id, frame.cliente === id)));
    if (frame.cola_extra) {
      const extra = document.createElement("span");
      extra.className = "extra";
      extra.textContent = "+" + frame.cola_extra;
      fila.append(extra);
    }
  }

  ((frame && frame.mostradores) || []).forEach((id, i) => {
    const puesto = document.createElement("div");
    puesto.className = "escritorio";
    if (id == null) {
      const hueco = document.createElement("span");
      hueco.className = "hueco";
      puesto.append(hueco);
    } else {
      puesto.append(persona(id, frame.cliente === id));
    }
    const mesa = document.createElement("span");
    mesa.className = "mesa";
    const nombre = document.createElement("span");
    nombre.className = "puesto";
    nombre.textContent = String(i + 1);
    puesto.append(mesa, nombre);
    desks.append(puesto);
  });

  root.querySelector("#reloj").textContent = reloj(frame ? frame.t : 0);
  root.querySelector("#detalle").textContent = frame ? frame.detalle : "";
  root.querySelector("#paso").textContent = total
    ? (index + 1) + " / " + total
    : "";
}

export default function (component) {
  const { data, parentElement } = component;
  const root = parentElement.querySelector(".escena");
  if (!root) return;

  const frames = (data && data.frames) || [];
  if (!root._estado) {
    root._estado = { index: 0, playing: false, speed: 1, corrida: null, timer: null, token: 0 };
  }
  const estado = root._estado;
  estado.frames = frames;
  estado.token += 1;
  const token = estado.token;

  if (estado.corrida !== (data && data.corrida)) {
    estado.corrida = data ? data.corrida : 0;
    estado.index = 0;
    estado.playing = Boolean(data && data.autoplay && frames.length > 1);
  }

  const delay = () => (estado.speed === 4 ? 160 : estado.speed === 2 ? 340 : 700);

  function parar() {
    if (estado.timer) {
      clearTimeout(estado.timer);
      estado.timer = null;
    }
  }

  function textoPlay() {
    const boton = root.querySelector("#play");
    const total = estado.frames.length;
    if (total <= 1) boton.textContent = "Listo";
    else if (estado.index >= total - 1) boton.textContent = "Otra vez";
    else boton.textContent = estado.playing ? "Pausa" : "Seguir";
  }

  function dibujar() {
    const actual = estado.frames;
    const frame = actual[estado.index] || actual[0];
    pintar(root, frame, actual.length, estado.index);
    textoPlay();
    root.querySelectorAll(".vel").forEach((boton) => {
      boton.classList.toggle("activo", Number(boton.dataset.vel) === estado.speed);
    });
  }

  function programar() {
    parar();
    if (!estado.playing) return;
    estado.timer = setTimeout(() => {
      const total = estado.frames.length;
      if (estado.index < total - 1) estado.index += 1;
      else estado.playing = false;
      dibujar();
      programar();
    }, delay());
  }

  root.querySelector("#play").onclick = () => {
    const total = estado.frames.length;
    if (total <= 1) return;
    if (estado.index >= total - 1) {
      estado.index = 0;
      estado.playing = true;
    } else {
      estado.playing = !estado.playing;
    }
    dibujar();
    programar();
  };
  root.querySelectorAll(".vel").forEach((boton) => {
    boton.onclick = () => {
      estado.speed = Number(boton.dataset.vel);
      dibujar();
      programar();
    };
  });

  dibujar();
  programar();

  return () => {
    if (estado.token === token) parar();
  };
}
"""


_FILA = st.components.v2.component(
    "fila_atencion",
    html=_HTML,
    css=_CSS,
    js=_JS,
)


def _marco_vacio(num_operadores: int) -> dict:
    return {
        "t": 0.0,
        "evento": "apertura",
        "detalle": "La oficina está lista. Ejecuta la simulación para ver la fila.",
        "cliente": None,
        "cola": [],
        "cola_extra": 0,
        "mostradores": [None] * num_operadores,
    }


def render_fila(trazas: list | None, num_operadores: int, corrida: int):
    """Dibuja la oficina y reproduce los movimientos guardados."""
    reales = trazas or []
    visibles = reales[:LIMITE_CUADROS]
    _FILA(
        data={
            "corrida": corrida,
            "autoplay": bool(reales),
            "frames": visibles or [_marco_vacio(num_operadores)],
        },
        key="fila_en_vivo",
        width="stretch",
        height=420,
    )
    omitidas = len(reales) - len(visibles)
    if omitidas > 0:
        st.caption(
            f"La animación muestra los primeros {len(visibles)} movimientos "
            f"de {len(reales)}. Las métricas usan la simulación completa."
        )
