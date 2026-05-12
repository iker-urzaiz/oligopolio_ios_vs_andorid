import math
import plotly.graph_objects as go
import streamlit as st

# ============================================================
# Simulador didáctico: lock-in en el duopolio Android-iOS
# Objetivo: complementar un trabajo de Microeconomía II.
# No predice el mercado real: ilustra switching costs y efectos de red.
# ============================================================

st.set_page_config(
    page_title="Duopolio Android-iOS | Simulador simple",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="collapsed",
)

CSS = """
<style>
:root{
    --bg:#f4f7fb;
    --panel:#ffffff;
    --panel2:#f8fafc;
    --text:#111827;
    --muted:#4b5563;
    --light:#6b7280;
    --border:#dbe3ef;
    --blue:#2563eb;
    --blue2:#1d4ed8;
    --green:#047857;
    --red:#b91c1c;
    --amber:#b45309;
    --shadow:0 18px 45px rgba(15,23,42,.08);
}

html, body, .stApp{
    background:var(--bg) !important;
    color:var(--text) !important;
}

.block-container{
    max-width:1180px;
    padding-top:1.25rem;
    padding-bottom:2.2rem;
}

/* Fuerza legibilidad general */
h1,h2,h3,h4,h5,h6,p,li,span,div,label,
[data-testid="stMarkdownContainer"],
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stWidgetLabel"] p,
[data-testid="stCaptionContainer"],
.stCaptionContainer{
    color:var(--text) !important;
    opacity:1 !important;
}

small, .muted, .hint{
    color:var(--muted) !important;
}

.hero{
    background:linear-gradient(135deg,#ffffff 0%,#eef5ff 100%);
    border:1px solid var(--border);
    border-radius:28px;
    padding:1.45rem 1.55rem;
    box-shadow:var(--shadow);
    margin-bottom:1rem;
    animation:fadeUp .45s ease both;
}

.card{
    background:var(--panel);
    border:1px solid var(--border);
    border-radius:24px;
    padding:1.1rem 1.2rem;
    box-shadow:var(--shadow);
    margin-bottom:1rem;
    animation:fadeUp .45s ease both;
}

.soft{
    background:var(--panel2);
    border:1px solid var(--border);
    border-radius:18px;
    padding:.95rem 1rem;
}

.badge{
    display:inline-block;
    background:#e8f0ff;
    color:#1744a7 !important;
    border:1px solid #c8d9ff;
    padding:.25rem .62rem;
    border-radius:999px;
    font-size:.85rem;
    font-weight:700;
    margin-right:.35rem;
    margin-bottom:.35rem;
}

.kpi{
    background:#ffffff;
    border:1px solid var(--border);
    border-radius:20px;
    padding:1rem;
    box-shadow:0 10px 25px rgba(15,23,42,.05);
    height:100%;
}
.kpi-title{font-size:.9rem;color:var(--muted)!important;font-weight:700;margin-bottom:.35rem;}
.kpi-value{font-size:2.05rem;font-weight:800;color:var(--text)!important;line-height:1.05;}
.kpi-note{font-size:.88rem;color:var(--light)!important;margin-top:.38rem;}

.callout{
    border-left:5px solid var(--blue);
    background:#eef5ff;
    border-radius:14px;
    padding:.85rem .95rem;
}

.warning{
    border-left:5px solid var(--amber);
    background:#fff7ed;
    border-radius:14px;
    padding:.85rem .95rem;
}

/* Widgets Streamlit */
.stSlider [data-baseweb="slider"]{
    padding-top:.35rem;
    padding-bottom:.25rem;
}
.stSlider p, .stRadio p, .stSelectbox p, .stNumberInput p{
    color:var(--text)!important;
    font-weight:700!important;
}

button[kind="primary"], .stButton > button{
    border-radius:14px !important;
    border:1px solid #c7d2fe !important;
    background:#ffffff !important;
    color:#1e3a8a !important;
    font-weight:800 !important;
    transition:transform .18s ease, box-shadow .18s ease, border-color .18s ease;
}
.stButton > button:hover{
    transform:translateY(-1px);
    box-shadow:0 10px 22px rgba(37,99,235,.14);
    border-color:#93c5fd !important;
}

/* Expanders con contraste */
div[data-testid="stExpander"]{
    background:#ffffff !important;
    border:1px solid var(--border) !important;
    border-radius:18px !important;
    box-shadow:0 8px 20px rgba(15,23,42,.04);
}
div[data-testid="stExpander"] summary,
div[data-testid="stExpander"] summary span,
div[data-testid="stExpander"] p,
div[data-testid="stExpander"] li{
    color:var(--text) !important;
}

hr{border-color:#dbe3ef!important;}

@keyframes fadeUp{
    from{opacity:0; transform:translateY(10px)}
    to{opacity:1; transform:translateY(0)}
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# -----------------------------
# Datos de contexto
# -----------------------------
# Cuotas orientativas globales. Se usan como contexto visual; deben citarse en el informe con la fuente real elegida.
ANDROID_SHARE = 72.07
IOS_SHARE = 27.52
CR2 = ANDROID_SHARE + IOS_SHARE
HHI = ANDROID_SHARE**2 + IOS_SHARE**2

# -----------------------------
# Funciones del modelo simple
# -----------------------------
def sigmoid(x: float) -> float:
    return 1 / (1 + math.exp(-max(min(x, 20), -20)))


def calcular_probabilidad(atractivo_rival: int, costes_cambio: int, efecto_red: int):
    """
    Modelo didáctico sencillo.
    - Atractivo rival: incentivos para cambiar.
    - Costes de cambio: fricciones de salida del ecosistema actual.
    - Efecto de red: fuerza que refuerza a la plataforma dominante.

    La puntuación neta se transforma en probabilidad con una función logística.
    """
    a = atractivo_rival / 10
    c = costes_cambio / 10
    n = efecto_red / 10

    # Ponderaciones simples y defendibles en clase:
    # el atractivo empuja al cambio; los costes y los efectos de red frenan.
    utilidad_neta = (1.35 * a) - (1.15 * c) - (0.85 * n)
    indice_cambio = sigmoid(3.0 * utilidad_neta)
    lockin = 1 - indice_cambio
    return utilidad_neta, indice_cambio, lockin


def clasificar_lockin(lockin):
    if lockin >= 0.70:
        return "Alto", "El usuario queda muy retenido por el ecosistema actual."
    if lockin >= 0.45:
        return "Medio", "Hay incentivos para cambiar, pero las fricciones siguen pesando."
    return "Bajo", "La plataforma rival resulta suficientemente atractiva para debilitar la retención."


def escenario_texto(indice_cambio, lockin, plataforma_actual, plataforma_rival):
    nivel, frase = clasificar_lockin(lockin)
    if lockin >= 0.70:
        conclusion = (
            f"Aunque {plataforma_rival} pueda resultar atractiva, los costes de cambio y los efectos de red hacen que "
            f"el usuario siga probablemente en {plataforma_actual}. Esto ayuda a explicar la estabilidad del duopolio."
        )
    elif lockin >= 0.45:
        conclusion = (
            f"El usuario está en una situación intermedia: podría valorar cambiar a {plataforma_rival}, "
            f"pero el ecosistema de {plataforma_actual} todavía actúa como barrera."
        )
    else:
        conclusion = (
            f"El cambio a {plataforma_rival} es plausible porque el atractivo de la alternativa supera parte de las barreras. "
            f"Esto muestra que el lock-in no es absoluto, pero sí condiciona la competencia."
        )
    return nivel, frase, conclusion


def bar_chart(indice_cambio, lockin):
    fig = go.Figure()
    fig.add_bar(x=["Tendencia simulada al cambio", "Índice de lock-in"], y=[indice_cambio * 100, lockin * 100],
                text=[f"{indice_cambio*100:.1f}%", f"{lockin*100:.1f}%"], textposition="auto")
    fig.update_layout(
        height=330,
        margin=dict(l=20, r=20, t=35, b=20),
        yaxis=dict(range=[0, 100], title="Porcentaje", gridcolor="rgba(148,163,184,.25)"),
        xaxis=dict(gridcolor="rgba(0,0,0,0)"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#111827", size=13),
        showlegend=False,
    )
    return fig


# -----------------------------
# Interfaz
# -----------------------------
st.markdown("""
<div class="hero">
  <h1 style="margin:0 0 .45rem 0;">📱 Simulador: Decisión del consumidor en el duopolio Android–iOS</h1>
  <p class="muted" style="font-size:1.02rem;margin-bottom:.75rem;">
  Simulación para complementar el trabajo de Microeconomía II. Su objetivo no es predecir el mercado real,
  sino visualizar por qué los costes de cambio y los efectos de red pueden mantener estable un duopolio digital.
  </p>
  <span class="badge">Duopolio</span>
  <span class="badge">Switching costs</span>
  <span class="badge">Lock-in</span>
  <span class="badge">Efectos de red</span>
  <span class="badge">Barreras de entrada</span>
</div>
""", unsafe_allow_html=True)

# Contexto del mercado
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("1) Contexto del mercado")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f'<div class="kpi"><div class="kpi-title">CR2 aproximado</div><div class="kpi-value">{CR2:.0f}%</div><div class="kpi-note">Android + iOS concentran prácticamente todo el mercado móvil.</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="kpi"><div class="kpi-title">HHI orientativo</div><div class="kpi-value">{HHI:.0f}</div><div class="kpi-note">Un HHI superior a 2.500 suele indicar alta concentración.</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="kpi"><div class="kpi-title">Idea clave</div><div class="kpi-value">2</div><div class="kpi-note">Dos ecosistemas dominantes: Android y iOS.</div></div>', unsafe_allow_html=True)
st.caption("Nota: cuotas orientativas usadas como referencia visual: Android 72.07% e iOS 27.52%.")
st.markdown('<div class="soft" style="margin-top:.75rem;"><b>Cómo leer el HHI:</b> el índice Herfindahl-Hirschman mide la concentración del mercado sumando los cuadrados de las cuotas de mercado. Un HHI superior a 2.500 suele considerarse propio de un mercado altamente concentrado. Aquí el valor es muy elevado porque el mercado está prácticamente repartido entre dos plataformas.</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Simulación principal
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("2) Simula una decisión de cambio")
st.markdown('<div class="callout"><b>Lectura rápida:</b> si el atractivo de la plataforma rival no compensa los costes de cambio y los efectos de red, el usuario tiende a permanecer en su ecosistema actual.</div>', unsafe_allow_html=True)

left, right = st.columns([0.95, 1.05], gap="large")

with left:
    plataforma_actual = st.radio("Plataforma actual del usuario", ["Android", "iOS"], horizontal=True)
    plataforma_rival = "iOS" if plataforma_actual == "Android" else "Android"

    st.markdown("#### Palancas del modelo")
    atractivo = st.slider(
        "Atractivo percibido de la plataforma rival",
        0, 10, 5,
        help="Cuánto mejor parece la otra plataforma en calidad, diseño, apps, servicios o precio."
    )
    st.caption("0 = nada atractiva · 10 = muy atractiva")

    costes = st.slider(
        "Costes de cambio del usuario",
        0, 10, 6,
        help="Fricciones de cambiar: datos, apps compradas, aprendizaje, accesorios y servicios asociados."
    )
    st.caption("0 = cambiar es fácil · 10 = cambiar es muy costoso")

    red = st.slider(
        "Fuerza de los efectos de red y ecosistema",
        0, 10, 7,
        help="Cuánto valor aporta que mucha gente, empresas y desarrolladores ya estén dentro de la plataforma dominante."
    )
    st.caption("0 = mercado muy abierto · 10 = ecosistema muy fuerte")

with right:
    utilidad, prob, lockin = calcular_probabilidad(atractivo, costes, red)
    nivel, frase, conclusion = escenario_texto(prob, lockin, plataforma_actual, plataforma_rival)

    k1, k2 = st.columns(2)
    with k1:
        st.markdown(f'<div class="kpi"><div class="kpi-title">Tendencia simulada al cambio a {plataforma_rival}</div><div class="kpi-value">{prob*100:.1f}%</div><div class="kpi-note">Índice conceptual, no probabilidad empírica real.</div></div>', unsafe_allow_html=True)
    with k2:
        st.markdown(f'<div class="kpi"><div class="kpi-title">Lock-in en {plataforma_actual}</div><div class="kpi-value">{lockin*100:.1f}%</div><div class="kpi-note">Nivel: {nivel}. {frase}</div></div>', unsafe_allow_html=True)

    st.plotly_chart(bar_chart(prob, lockin), use_container_width=True)
    st.markdown(f'<div class="soft"><b>Conclusión económica:</b><br>{conclusion}</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Explicación del modelo en desplegable
st.markdown('<div class="card">', unsafe_allow_html=True)
with st.expander("📘 Cómo funciona el modelo usado", expanded=False):
    st.markdown("""
    Este simulador utiliza un modelo conceptual muy sencillo de decisión del consumidor.

    La idea es que un usuario cambia de sistema operativo si el beneficio esperado de la plataforma rival supera las barreras de salida de su plataforma actual.

    **Variables usadas:**

    1. **Atractivo percibido de la plataforma rival**: resume calidad, precio, apps, servicios e integración.
    2. **Costes de cambio** (*switching costs*): incluye pérdida de compras previas, transferencia de datos, aprendizaje del nuevo sistema y compatibilidad con dispositivos o servicios.
    3. **Efectos de red y ecosistema**: reflejan que una plataforma es más valiosa cuanto más usuarios, desarrolladores, apps y servicios tiene alrededor.

    El modelo calcula una **utilidad neta de cambio**:

    \[
    U = 1.35A - 1.15C - 0.85N
    \]

    Donde:

    - \(A\) = atractivo de la plataforma rival.
    - \(C\) = costes de cambio.
    - \(N\) = efectos de red y ecosistema.

    Después, esa utilidad se transforma en un índice conceptual entre 0% y 100%. 

    **Importante:** los pesos son genéricos y didácticos. No pretenden medir exactamente la realidad; solo representan una idea microeconómica: el atractivo de una alternativa puede incentivar el cambio, pero los costes de cambio y los efectos de red pueden frenarlo.
    """)

with st.expander("⚠️ Límites del simulador", expanded=False):
    st.markdown("""
    Este simulador no es una predicción real del mercado Android-iOS. Es una herramienta didáctica para visualizar conceptos del trabajo.

    Sus principales límites son:

    - No usa datos reales de consumidores.
    - No distingue por países, renta, edad o segmentos de consumidores.
    - No modeliza decisiones estratégicas completas de Apple y Google.

    Por tanto, debe usarse como complemento del trabajo escrito, no como prueba empírica definitiva.
    """)

with st.expander("🤖 Uso de IA en esta herramienta", expanded=False):
    st.markdown("""
    La IA se ha utilizado como apoyo para estructurar el modelo, simplificar la explicación económica y generar una interfaz visual clara.
    La función del simulador es didáctica: ayudar a comunicar de forma intuitiva cómo los costes de cambio y los efectos de red refuerzan la estabilidad del duopolio Android-iOS.
    """)
st.markdown('</div>', unsafe_allow_html=True)

# Frase para el informe
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("3) Objetivo del simulador")
st.markdown(f"""
<div class="warning">
El objetivo de este simulador es complementar el trabajo escrito mediante una representación visual y sencilla del lock-in o fidelización en el duopolio Android-iOS. La herramienta permite observar cómo el atractivo de una plataforma rival puede verse limitado por los costes de cambio y los efectos de red. Por tanto, no pretende predecir el mercado real, sino ayudar a explicar por qué este duopolio puede mantenerse en el tiempo: la competencia existe, pero está condicionada por la dependencia de los usuarios respecto a sus ecosistemas digitales.
</div>
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Pie
st.caption("Simulador didáctico para trabajo de Microeconomía II")
