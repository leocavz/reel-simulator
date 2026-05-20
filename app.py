import streamlit as st
import csv
import json
import os
import re
import math
import urllib.request
import urllib.error
from datetime import date, timedelta
from pathlib import Path
from collections import Counter
import anthropic

# ── Detección de idioma ──────────────────────────────────
_ES = {"que","de","la","el","en","los","las","un","una","con","por","para","del","este","esto","como","pero","más","muy","hay","ser","fue","son","están","tiene","cuando","también","porque","sobre","entre","sin","ya","todo","qué","cómo","mi","me","te","tu","le","su","si","no","es","se","al","lo","sus","era","una"}
_EN = {"the","is","are","you","i","it","and","of","to","in","that","for","on","with","this","they","be","have","at","from","or","but","an","not","what","your","all","can","her","him","just","so","if","about","who","get","do","my","we","when","how","said","know","think","like","up","go","there","one","out","people","will"}

def detectar_idioma(texto):
    words = set(re.findall(r"[a-zA-Z]{2,}", texto.lower()))
    es = len(words & _ES)
    en = len(words & _EN)
    return "en" if en > es else "es"

# ── Config ──────────────────────────────────────────────
st.set_page_config(
    page_title="Simulador de Reels · Leo Cavz",
    page_icon="🎬",
    layout="centered",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;600;700;800;900&family=Barlow:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Barlow', sans-serif;
}

.stApp {
    background-color: #0a0a0a;
    color: #ffffff;
}

#MainMenu, footer, header { visibility: hidden; }

.block-container {
    padding-top: 3rem;
    padding-bottom: 4rem;
    max-width: 760px;
}

p, li, label, .stMarkdown, div { color: #e0e0e0 !important; }

h1 {
    font-family: 'Barlow Condensed', sans-serif !important;
    font-size: 3rem !important;
    font-weight: 900 !important;
    color: #ffffff !important;
    letter-spacing: 0.05em !important;
    text-transform: uppercase !important;
    margin-bottom: 0 !important;
}

h2, h3 {
    font-family: 'Barlow Condensed', sans-serif !important;
    font-weight: 700 !important;
    color: #ffffff !important;
    letter-spacing: 0.04em !important;
    text-transform: uppercase !important;
}

.stCaption { color: #555555 !important; font-size: 0.82rem !important; }

.stTextArea textarea {
    background: #141414 !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 4px !important;
    color: #e0e0e0 !important;
    font-family: 'Barlow', sans-serif !important;
    font-size: 0.95rem !important;
    padding: 1rem !important;
    outline: none !important;
    box-shadow: none !important;
}
.stTextArea textarea:focus {
    border-color: #555555 !important;
    outline: none !important;
    box-shadow: none !important;
}
.stTextArea > div {
    border: none !important;
    box-shadow: none !important;
}
.stTextArea label { color: #888 !important; font-size: 0.8rem !important; text-transform: uppercase !important; letter-spacing: 0.08em !important; }

.stButton > button[kind="primary"] {
    background-color: #ffffff !important;
    color: #0a0a0a !important;
    border: none !important;
    border-radius: 2px !important;
    padding: 0.75rem 2rem !important;
    font-family: 'Barlow Condensed', sans-serif !important;
    font-size: 1rem !important;
    font-weight: 800 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    transition: background 0.2s, transform 0.1s !important;
}
.stButton > button[kind="primary"] p {
    color: #0a0a0a !important;
}
.stButton > button[kind="primary"]:hover {
    background-color: #cccccc !important;
    transform: translateY(-1px) !important;
}

[data-testid="stMetric"] {
    background: #141414;
    border: 1px solid #222;
    border-radius: 4px;
    padding: 1.2rem 1.5rem;
}
[data-testid="stMetricValue"] {
    font-family: 'Barlow Condensed', sans-serif !important;
    font-size: 3rem !important;
    font-weight: 900 !important;
    color: #ffffff !important;
}
[data-testid="stMetricLabel"] { color: #666 !important; text-transform: uppercase !important; font-size: 0.75rem !important; letter-spacing: 0.1em !important; }

.stProgress > div > div {
    background-color: #ffffff !important;
    border-radius: 0 !important;
}
.stProgress > div {
    background-color: #222222 !important;
    border-radius: 0 !important;
    height: 4px !important;
}

.streamlit-expanderHeader {
    background: #141414 !important;
    font-family: 'Barlow Condensed', sans-serif !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    color: #ffffff !important;
    letter-spacing: 0.05em !important;
    text-transform: uppercase !important;
    border: 1px solid #222 !important;
    border-radius: 2px !important;
}
.streamlit-expanderContent {
    background: #0f0f0f !important;
    border-left: 2px solid #333 !important;
    padding-left: 1rem !important;
    color: #aaaaaa !important;
}

hr {
    border-color: #1f1f1f !important;
    margin: 2rem 0 !important;
}

.stSlider [data-baseweb="slider"] [data-testid="stThumbValue"] { color: #ffffff !important; }
.stSlider label { color: #888 !important; text-transform: uppercase !important; font-size: 0.78rem !important; letter-spacing: 0.08em !important; }

.reel-card {
    background: #111111;
    border-left: 2px solid #ffffff;
    padding: 0.9rem 1.2rem;
    margin-bottom: 0.6rem;
    border-radius: 2px;
}
.reel-views {
    font-family: 'Barlow Condensed', sans-serif;
    font-weight: 800;
    font-size: 1.1rem;
    color: #ffffff;
    letter-spacing: 0.03em;
}

.brand-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 0.5rem;
}
.brand-cross {
    font-size: 1.8rem;
    color: #ffffff;
    font-weight: 300;
    line-height: 1;
}
.brand-name {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 1.1rem;
    font-weight: 700;
    color: #555555;
    letter-spacing: 0.2em;
    text-transform: uppercase;
}

.stAlert { background: #141414 !important; border-radius: 2px !important; }

.pred-card {
    background: #111;
    border: 1px solid #222;
    padding: 1.5rem;
    border-radius: 2px;
    margin-bottom: 1rem;
}
.pred-label {
    color: #555;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 0.5rem;
}
.pred-range {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 2.8rem;
    font-weight: 900;
    color: #fff;
    letter-spacing: 0.02em;
}
.pred-sub {
    color: #555;
    font-size: 0.85rem;
    margin-top: 0.3rem;
}
</style>
""", unsafe_allow_html=True)

BASE = Path(__file__).parent
CSV_FILE = BASE / "leo_cavz_reels.csv"
TRANSCRIPTS_DIR = BASE / "transcripts"
COMP_CSV = BASE / "competidores_reels.csv"
COMP_TRANS_DIR = BASE / "competidores" / "transcripts"
REFS_DIR = BASE / "referencias"
NOTION_DB_ID = "361ad8c7-557b-80c2-9ff9-fac8b2098885"

def proximo_jueves():
    hoy = date.today()
    dias = (3 - hoy.weekday()) % 7
    return str(hoy + timedelta(days=dias or 7))

def push_to_notion(titulo, script_text, semana, ref_url=""):
    token = st.secrets.get("NOTION_TOKEN", os.environ.get("NOTION_TOKEN", ""))
    if not token:
        raise ValueError("NOTION_TOKEN no configurado en secrets")
    body = {
        "parent": {"database_id": NOTION_DB_ID},
        "properties": {
            "Título": {"title": [{"text": {"content": titulo[:255]}}]},
            "Script": {"rich_text": [{"text": {"content": script_text[:2000]}}]},
            "Estado": {"status": {"name": "Listo para grabar"}},
            "Formato": {"select": {"name": "Video"}},
            "Plataforma": {"multi_select": [{"name": "Ig"}]},
            "Fecha de Publicación": {"date": {"start": proximo_jueves()}},
            "Semana": {"select": {"name": semana}},
        },
    }
    if ref_url.strip():
        body["properties"]["Referencia"] = {"url": ref_url.strip()}
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        "https://api.notion.com/v1/pages",
        data=data,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as r:
        result = json.loads(r.read())
    return result.get("url", "")

STOP_WORDS = {
    "para","como","pero","más","muy","hay","que","con","los","las","una","del",
    "este","esto","también","porque","sobre","entre","todo","cuando","tiene",
    "están","esta","este","from","that","with","this","they","have","were",
    "your","what","about","just","like","know","think","people","there","their",
    "would","could","should","which","donde","quien","algo","nada","cada",
    "mismo","misma","otros","otras","otro","otra","mucho","mucha","poco",
    "bien","mal","hacer","hace","decir","dice","quiero","quiere","vamos",
    "todos","todas","somos","puedo","puedes","puede","veces","cosas","cosa",
    "time","going","dont","doesnt","cant","wont","said","says","being",
    "really","actually","basically","literally","guys","okay","yeah","when",
    "then","than","them","were","these","those","some","here","also","even",
    "still","back","after","into","only","over","such","most","more","many"
}

@st.cache_data
def cargar_datos():
    with open(CSV_FILE) as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        try: r["_views"] = int(r["views"])
        except: r["_views"] = 0
        try: r["_saves"] = int(r["saves"]) if r.get("saves") else 0
        except: r["_saves"] = 0
        try: r["_shares"] = int(r["shares"]) if r.get("shares") else 0
        except: r["_shares"] = 0
        try: r["_reach"] = int(r["reach"]) if r.get("reach") else 0
        except: r["_reach"] = 0
        try: r["_avg_watch"] = int(r["avg_watch_ms"]) / 1000 if r.get("avg_watch_ms") else 0
        except: r["_avg_watch"] = 0
        r["_save_rate"] = r["_saves"] / r["_reach"] * 100 if r["_reach"] > 0 else 0
        r["_share_rate"] = r["_shares"] / r["_reach"] * 100 if r["_reach"] > 0 else 0
        r["_cuenta"] = "leo_cavz"
        code = r["shortCode"]
        txt = TRANSCRIPTS_DIR / f"{code}.txt"
        r["_transcript"] = txt.read_text(encoding="utf-8") if txt.exists() else ""
    return sorted(rows, key=lambda r: r["_views"], reverse=True)

@st.cache_data
def cargar_competidores():
    if not COMP_CSV.exists():
        return []
    with open(COMP_CSV) as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        try: r["_views"] = int(r["views"]) if r.get("views") else 0
        except: r["_views"] = 0
        r["_saves"] = 0; r["_shares"] = 0; r["_reach"] = 0
        r["_avg_watch"] = 0; r["_save_rate"] = 0; r["_share_rate"] = 0
        r["_cuenta"] = r.get("cuenta", "competidor")
        code = r["shortCode"]
        txt = COMP_TRANS_DIR / f"{code}.txt"
        r["_transcript"] = txt.read_text(encoding="utf-8") if txt.exists() else r.get("transcript", "")
    return [r for r in rows if r["_transcript"].strip()]

@st.cache_data
def construir_idf():
    rows = cargar_datos()
    comp_rows = cargar_competidores()
    all_transcripts = [r["_transcript"] for r in rows + comp_rows if r.get("_transcript")]
    N = len(all_transcripts)
    df = Counter()
    for txt in all_transcripts:
        words = set(re.findall(r"[a-záéíóúñA-ZÁÉÍÓÚÑa-z]{4,}", txt.lower())) - STOP_WORDS
        df.update(words)
    return {w: math.log(N / max(c, 1)) for w, c in df.items()}

def _palabras_grupo(reels):
    words = []
    for r in reels:
        words.extend(re.findall(r"[a-záéíóúñA-ZÁÉÍÓÚÑa-z]{4,}", r["_transcript"].lower()))
    return Counter(w for w in words if w not in STOP_WORDS)

@st.cache_data
def extraer_patrones_leo():
    """Patrones exclusivos del top 1% de Leo vs su bottom 75%."""
    rows = cargar_datos()
    con_transcript = [r for r in rows if r.get("_transcript") and r["_views"] > 0]
    if len(con_transcript) < 8:
        return [], []
    con_transcript.sort(key=lambda r: r["_views"], reverse=True)
    n = len(con_transcript)
    top = con_transcript[:max(int(n * 0.01), 2)]
    bottom = con_transcript[min(int(n * 0.75), n - 2):]

    top_cnt = _palabras_grupo(top)
    bot_cnt = _palabras_grupo(bottom)
    n_top, n_bot = max(len(top), 1), max(len(bottom), 1)

    top_char = [
        w for w, c in top_cnt.most_common(80)
        if top_cnt[w] / n_top > bot_cnt.get(w, 0) / n_bot * 1.5 and c >= 2
    ][:20]
    bot_char = [
        w for w, c in bot_cnt.most_common(80)
        if bot_cnt[w] / n_bot > top_cnt.get(w, 0) / n_top * 1.5 and c >= 2
    ][:20]
    return top_char, bot_char

@st.cache_data
def extraer_patrones_nicho():
    """Patrones del top 10% de competidores (reels de mayor alcance en el nicho) vs bottom de Leo."""
    rows = cargar_datos()
    comp_rows = cargar_competidores()
    comp_con_t = [r for r in comp_rows if r.get("_transcript") and r["_views"] > 0]
    if not comp_con_t:
        return []
    comp_con_t.sort(key=lambda r: r["_views"], reverse=True)
    top_comp = comp_con_t[:max(int(len(comp_con_t) * 0.10), 5)]

    leo_con_t = [r for r in rows if r.get("_transcript") and r["_views"] > 0]
    leo_con_t.sort(key=lambda r: r["_views"], reverse=True)
    bottom_leo = leo_con_t[min(int(len(leo_con_t) * 0.75), len(leo_con_t) - 2):]

    top_cnt = _palabras_grupo(top_comp)
    bot_cnt = _palabras_grupo(bottom_leo)
    n_top, n_bot = max(len(top_comp), 1), max(len(bottom_leo), 1)

    return [
        w for w, c in top_cnt.most_common(100)
        if top_cnt[w] / n_top > bot_cnt.get(w, 0) / n_bot * 1.5 and c >= 3
    ][:20]

def similares_idf(script, rows, comp_rows, idf):
    script_words = set(re.findall(r"[a-záéíóúñA-ZÁÉÍÓÚÑa-z]{4,}", script.lower())) - STOP_WORDS
    resultados = []
    for r in (rows + comp_rows):
        if not r.get("_transcript"):
            continue
        t_words = set(re.findall(r"[a-záéíóúñA-ZÁÉÍÓÚÑa-z]{4,}", r["_transcript"].lower())) - STOP_WORDS
        matching = script_words & t_words
        if len(matching) < 2:
            continue
        score_sim = sum(idf.get(w, 1.0) for w in matching)
        resultados.append((score_sim, r))
    return sorted(resultados, key=lambda x: x[0], reverse=True)[:8]

def calcular_prediccion(sim_reels):
    views = sorted([r["_views"] for _, r in sim_reels if r["_views"] > 0])
    if len(views) < 2:
        return None
    n = len(views)
    return {
        "min": views[0],
        "p25": views[max(n // 4 - 1, 0)],
        "mediana": views[n // 2],
        "p75": views[min(3 * n // 4, n - 1)],
        "max": views[-1],
        "n": n,
    }

def fmt_views(v):
    if v >= 1_000_000:
        return f"{v / 1_000_000:.1f}M"
    elif v >= 1_000:
        return f"{round(v / 1_000):.0f}k"
    return str(v)

def analizar_con_claude(client, script, sim_reels, top_patterns, bot_patterns, nicho_patterns, idioma, duracion):
    context_reels = ""
    for i, (_, r) in enumerate(sim_reels[:6], 1):
        cuenta = r.get("_cuenta", "")
        views = r["_views"]
        hook = r["_transcript"][:220].replace("\n", " ")
        context_reels += f"\n{i}. @{cuenta} — {views:,} views:\n\"{hook}...\"\n"

    idioma_instruccion = (
        "El script está en INGLÉS. Analiza en español."
        if idioma == "en" else "El script está en español."
    )
    dur_str = (
        f"Duración estimada: {duracion} seg (zona óptima del nicho: 30-55 seg)"
        if duracion > 0 else "Duración no especificada (zona óptima: 30-55 seg)"
    )

    prompt = f"""Eres el analista de contenido de Leo Cavz (@leocavz, 557k seguidores en Instagram, México).
Tu trabajo: analizar scripts de reels basándote en datos reales de rendimiento, no en reglas genéricas.
{idioma_instruccion}
{dur_str}

SCRIPT A ANALIZAR:
---
{script}
---

REELS SIMILARES EN LA BASE DE DATOS (ordenados por similitud semántica con el script):
{context_reels if context_reels else "No se encontraron reels con tema similar."}

PATRONES DEL TOP 1% DE LEO (sus 2 reels con +500k views):
{', '.join(top_patterns[:15]) if top_patterns else 'datos insuficientes'}

PATRONES DEL TOP 10% DEL NICHO (top performers de @salomondrin, @hormozi, @jaimehigueraes, @imangadzhireels, @robthebank — reels de hasta 7M views):
{', '.join(nicho_patterns[:15]) if nicho_patterns else 'datos insuficientes'}

PALABRAS Y CONCEPTOS MÁS COMUNES EN EL BAJO RENDIMIENTO DE LEO:
{', '.join(bot_patterns[:15]) if bot_patterns else 'datos insuficientes'}

Analiza comparando el script contra los datos reales. No inventes reglas genéricas.
Si el script tiene similitud con reels reales, di cuáles y qué tienen en común o diferente.
Sé directo y específico — Leo no quiere fluff.

Responde EXACTAMENTE en este formato en español:

PREDICCIÓN: [ALTO / MEDIO / BAJO] — [1 línea concreta explicando por qué, con referencia a los datos]

QUÉ FUNCIONA:
• [punto específico con referencia a reels reales si aplica]
• [punto específico]

QUÉ FALLA:
• [punto específico con lo que hacen diferente los reels de alto rendimiento]
• [punto específico]

CAMBIO PRIORITARIO:
[Una sola acción concreta. Sin intro, sin rodeos. Si hay que reescribir el hook, di exactamente cómo.]"""

    with client.messages.stream(
        model="claude-haiku-4-5-20251001",
        max_tokens=750,
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        for text in stream.text_stream:
            yield text

# ── Session state ────────────────────────────────────────
defaults = {
    "script": "", "duracion": 0, "analizado": False,
    "analisis_result": "", "sim_cached": [], "pred_cached": None,
    "last_analyzed_script": "",
    "reescrito": "", "notion_guardado": False,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── UI ───────────────────────────────────────────────────
st.markdown("""
<div class="brand-header">
    <span class="brand-cross">†</span>
    <span class="brand-name">Tribu · Leo Cavz</span>
</div>
<h1>Simulador de Reels</h1>
""", unsafe_allow_html=True)
st.caption("Análisis comparativo contra 434 transcripts reales · IA + datos de rendimiento")
st.divider()

script = st.text_area(
    "Script del reel",
    height=280,
    placeholder="Pega aquí lo que vas a decir en tu reel (el script hablado)...",
    value=st.session_state.script,
)
st.markdown("<br>", unsafe_allow_html=True)
duracion = st.slider("Duración estimada (segundos)", 0, 120, st.session_state.duracion, step=5,
                     help="Pon 0 si no sabes aún")
st.markdown("<br>", unsafe_allow_html=True)

if st.button("Analizar reel", type="primary", use_container_width=True) and script.strip():
    st.session_state.script = script
    st.session_state.duracion = duracion
    st.session_state.analizado = True
    st.session_state.analisis_result = ""  # force re-analysis

if st.session_state.analizado and st.session_state.script.strip():
    script = st.session_state.script
    duracion = st.session_state.duracion

    rows = cargar_datos()
    comp_rows = cargar_competidores()
    idf = construir_idf()
    top_patterns, bot_patterns = extraer_patrones_leo()
    nicho_patterns = extraer_patrones_nicho()
    idioma = detectar_idioma(script)

    # Recalculate only when script changed
    if script != st.session_state.last_analyzed_script:
        sim = similares_idf(script, rows, comp_rows, idf)
        pred = calcular_prediccion(sim)
        st.session_state.sim_cached = sim
        st.session_state.pred_cached = pred
        st.session_state.last_analyzed_script = script
        st.session_state.reescrito = ""
        st.session_state.notion_guardado = False
    else:
        sim = st.session_state.sim_cached
        pred = st.session_state.pred_cached

    st.divider()

    # ── Predicted views range ────────────────────────────
    if pred:
        st.markdown(f"""
        <div class="pred-card">
            <div class="pred-label">ALCANCE ESTIMADO · {pred['n']} reels similares en la base de datos</div>
            <div class="pred-range">{fmt_views(pred['p25'])} — {fmt_views(pred['p75'])} views</div>
            <div class="pred-sub">mediana {fmt_views(pred['mediana'])} · rango completo {fmt_views(pred['min'])}–{fmt_views(pred['max'])}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="pred-card">
            <div class="pred-label">ALCANCE ESTIMADO</div>
            <div style="color:#555;font-size:0.9rem">No hay suficientes reels similares para estimar — tema muy diferente a lo publicado antes</div>
        </div>
        """, unsafe_allow_html=True)

    idioma_label = "🇺🇸 Inglés detectado — análisis en español" if idioma == "en" else "🇲🇽 Español detectado"
    st.caption(idioma_label)

    # ── Claude analysis ──────────────────────────────────
    st.divider()
    st.subheader("Análisis comparativo")

    if not st.session_state.analisis_result:
        try:
            client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
            placeholder = st.empty()
            full_text = ""
            for chunk in analizar_con_claude(
                client, script, sim, top_patterns, bot_patterns, nicho_patterns, idioma, duracion
            ):
                full_text += chunk
                placeholder.markdown(full_text + "▌")
            placeholder.markdown(full_text)
            st.session_state.analisis_result = full_text
        except Exception as e:
            st.error(f"Error en análisis: {e}")
    else:
        st.markdown(st.session_state.analisis_result)

    # ── Reescritura ──────────────────────────────────────
    st.divider()
    st.subheader("✍️ Reescribir con IA")

    if st.button("Reescribir este script", use_container_width=True):
        top3_ejemplos = "\n\n".join(
            f"@{r['_cuenta']} — {r['_views']:,} views:\n{r['_transcript'][:350]}"
            for _, r in (sim or [])[:3]
            if r.get("_transcript")
        )
        idioma_instruccion = (
            "El script original está en INGLÉS. Reescríbelo completamente en ESPAÑOL mexicano con el tono de Leo — no es traducción literal, es adaptación."
            if idioma == "en"
            else "El script original está en español."
        )

        prompt_rewrite = f"""Eres el asistente de contenido de Leo Cavz, creador mexicano con 557k seguidores en Instagram.
Su estilo es directo, coloquial, provocador y usa lenguaje mexicano auténtico (wey, pendejo, etc.).
{idioma_instruccion}

PATRONES DEL TOP 1% DE LEO (sus 2 reels con +500k views — lo que funciona para SU audiencia):
{', '.join(top_patterns[:12]) if top_patterns else 'N/A'}

PATRONES DEL NICHO (top 10% de @salomondrin, @hormozi, @jaimehigueraes, @imangadzhireels, @robthebank — hasta 7M views):
{', '.join(nicho_patterns[:12]) if nicho_patterns else 'N/A'}

Reels similares con buen rendimiento (referencia de hook y estructura):
{top3_ejemplos if top3_ejemplos else "Sin similares directos."}

Script original:
{script}

Análisis previo:
{st.session_state.analisis_result[:400] if st.session_state.analisis_result else ""}

Aplica los patrones del top 1% de Leo y del nicho. Mantén el mensaje central.
Devuelve SOLO el script hablado. Sin explicaciones, sin encabezados."""

        with st.spinner("Reescribiendo..."):
            try:
                client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
                response = client.messages.create(
                    model="claude-haiku-4-5-20251001",
                    max_tokens=1024,
                    messages=[{"role": "user", "content": prompt_rewrite}],
                )
                st.session_state.reescrito = response.content[0].text
                st.session_state.notion_guardado = False
            except Exception as e:
                st.error(f"Error: {e}")

    if st.session_state.reescrito:
        reescrito = st.session_state.reescrito
        st.markdown(
            f'<div style="background:#111;border-left:2px solid #fff;padding:1.2rem;border-radius:2px;'
            f'font-family:\'Barlow\',sans-serif;color:#e0e0e0;line-height:1.7;white-space:pre-wrap">'
            f'{reescrito}</div>',
            unsafe_allow_html=True,
        )

        # ── Guardar en Banco de Contenido ────────────────────
        st.divider()
        st.subheader("📋 Guardar en Banco de Contenido")
        titulo_sugerido = reescrito.strip().split("\n")[0][:100].lstrip("- •*#").strip()
        col1, col2 = st.columns([3, 1])
        with col1:
            titulo_notion = st.text_input("Título", value=titulo_sugerido, key="notion_titulo")
        with col2:
            semana_notion = st.selectbox("Semana", ["s1", "s2", "s3", "s4"], key="notion_semana")
        ref_notion = st.text_input(
            "URL de referencia (opcional)",
            placeholder="https://www.instagram.com/p/...",
            key="notion_ref",
        )

        if st.session_state.notion_guardado:
            st.success(f"Guardado en Notion — agendado para grabar el {proximo_jueves()}")
        elif st.button("Guardar en Banco de Contenido", type="primary", use_container_width=True):
            with st.spinner("Guardando en Notion..."):
                try:
                    notion_url = push_to_notion(titulo_notion, reescrito, semana_notion, ref_notion)
                    st.session_state.notion_guardado = True
                    st.success(f"Guardado — agendado para grabar el {proximo_jueves()}")
                    if notion_url:
                        st.markdown(f"[Abrir en Notion]({notion_url})")
                except Exception as e:
                    st.error(f"Error al guardar: {e}")

    # ── Similar reels ────────────────────────────────────
    if sim:
        st.divider()
        st.subheader("Reels similares en el nicho")
        for _, r in sim[:5]:
            hook = r["_transcript"][:120]
            cuenta = r.get("_cuenta", "")
            es_leo = cuenta == "leo_cavz"
            border_color = "#ffffff" if es_leo else "#444444"
            save_str = f"{r['_save_rate']:.1f}% saves" if r.get("_save_rate") else ""
            share_str = f"{r['_share_rate']:.1f}% shares" if r.get("_share_rate") else ""
            watch_str = f"{r['_avg_watch']:.0f}s retención" if r.get("_avg_watch") else ""
            metrics = " · ".join(filter(None, [save_str, share_str, watch_str]))
            st.markdown(f"""
            <div class="reel-card" style="border-left-color:{border_color}">
                <span class="reel-views">{int(r['_views']):,} views</span>
                <span style="color:#666;font-size:0.8rem;margin-left:8px">{metrics}</span>
                <span style="color:#555;font-size:0.78rem;margin-left:8px">@{cuenta}</span><br>
                <span style="color:#555;font-size:0.85rem">{hook}…</span>
            </div>
            """, unsafe_allow_html=True)
