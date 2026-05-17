import streamlit as st
import csv
import re
from pathlib import Path
from collections import Counter
import anthropic

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

/* Fondo negro */
.stApp {
    background-color: #0a0a0a;
    color: #ffffff;
}

/* Ocultar header y footer de Streamlit */
#MainMenu, footer, header { visibility: hidden; }

/* Contenedor */
.block-container {
    padding-top: 3rem;
    padding-bottom: 4rem;
    max-width: 760px;
}

/* Texto general blanco */
p, li, label, .stMarkdown, div { color: #e0e0e0 !important; }

/* Título */
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

/* Caption */
.stCaption { color: #555555 !important; font-size: 0.82rem !important; }

/* Textarea */
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

/* Botón */
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

/* Métrica */
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

/* Progress bar */
.stProgress > div > div {
    background-color: #ffffff !important;
    border-radius: 0 !important;
}
.stProgress > div {
    background-color: #222222 !important;
    border-radius: 0 !important;
    height: 4px !important;
}

/* Expanders */
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

/* Divider */
hr {
    border-color: #1f1f1f !important;
    margin: 2rem 0 !important;
}

/* Slider */
.stSlider [data-baseweb="slider"] [data-testid="stThumbValue"] { color: #ffffff !important; }
.stSlider label { color: #888 !important; text-transform: uppercase !important; font-size: 0.78rem !important; letter-spacing: 0.08em !important; }

/* Cards reels */
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

/* Logo header */
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

/* Warning/success/error en dark */
.stAlert { background: #141414 !important; border-radius: 2px !important; }
</style>
""", unsafe_allow_html=True)

BASE = Path(__file__).parent
CSV_FILE = BASE / "leo_cavz_reels.csv"
TRANSCRIPTS_DIR = BASE / "transcripts"

# Palabras distintivas extraídas SOLO de transcripts virales vs no virales
PALABRAS_VIRALES = {
    # Multiplicadores muy altos en virales (análisis transcript-only)
    "comentarios": 12, "despierto": 12, "marketing": 10, "modelo": 10,
    "dólares": 9, "dinero": 9, "millonario": 9, "negocios": 8,
    "negocio": 8, "disciplina": 9, "proceso": 8, "banco": 8,
    # Temas de identidad y crítica — alta frecuencia en top reels
    "estoicismo": 10, "estafa": 9, "universidad": 8, "curso": 8,
    "bancarrota": 9, "mamón": 8, "pendejo": 7, "verga": 6,
    # Temas de mentalidad y sistema
    "monk mode": 10, "winter arc": 9, "manifestar": 7,
    "libro": 8, "conocimiento": 8, "vida": 6, "sígueme": 6,
    # Conexión con audiencia
    "wey": 5, "pinche": 4, "novia": 6,
}

# Hooks extraídos de transcripts virales reales (no captions)
HOOK_PATRONES = [
    (r"en los últimos", 15, "'En los últimos X...' — tu formato más viral (611k views)"),
    (r"hablemos de", 12, "'Hablemos de...' — intro directa (hasta 324k views)"),
    (r"¿es posible", 12, "'¿Es posible...?' — pregunta retórica (555k views)"),
    (r"una de las cosas que", 10, "'Una de las cosas que...' — observación fuerte (527k views)"),
    (r"solo los pendejos", 10, "'Solo los pendejos...' — confrontacional (200k views)"),
    (r"hace \w+ (año|mes|semana)", 10, "historia con tiempo específico (218k views)"),
    (r"¿sabes (lo que|qué|cuánto)", 10, "pregunta directa al espectador"),
    (r"la verga", 8, "arranque directo con impacto (198k views)"),
]

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
        code = r["shortCode"]
        txt = TRANSCRIPTS_DIR / f"{code}.txt"
        r["_transcript"] = txt.read_text(encoding="utf-8") if txt.exists() else ""
    return sorted(rows, key=lambda r: r["_views"], reverse=True)

def score_hook(script):
    primera = script.strip().split("\n")[0].lower()[:200]
    score, notas = 0, []
    for patron, pts, nombre in HOOK_PATRONES:
        if re.search(patron, primera):
            score += pts
            notas.append(("✅", f"Hook tipo *{nombre}*"))
            break
    if not notas:
        if "?" in primera:
            score += 6
            notas.append(("⚠️", "Pregunta en el hook — funciona pero no es tu patrón más fuerte"))
        else:
            notas.append(("❌", "El hook no coincide con tus patrones virales"))
            notas.append(("💡", "Prueba: *'En los últimos X...'* / *'Hablemos de...'* / *'¿Es posible...?'*"))
    return min(score, 25), notas

def score_tema(script):
    texto = script.lower()
    score, temas = 0, []
    for palabra, peso in PALABRAS_VIRALES.items():
        if palabra in texto:
            score += peso
            temas.append(palabra)
    score = min(score, 35)
    notas = []
    if temas:
        notas.append(("✅", f"Temas virales detectados en el script: *{', '.join(temas[:6])}*"))
    else:
        notas.append(("⚠️", "No detecté temas de alto rendimiento en el contenido"))
        notas.append(("💡", "Tus temas más fuertes: dinero, disciplina, negocios, comentarios, despierto"))
    return score, notas

def score_duracion(duracion):
    if duracion == 0:
        return 0, [("ℹ️", "No indicaste duración — zona óptima: 30-55 seg")]
    if 30 <= duracion <= 55:
        return 15, [("✅", f"Duración ideal ({duracion} seg)")]
    elif 55 < duracion <= 70:
        return 8, [("⚠️", f"Un poco largo ({duracion} seg) — intenta recortar a menos de 55 seg")]
    else:
        return 0, [("❌", f"Fuera del rango óptimo ({duracion} seg) — recorta a 30-55 seg")]

def score_cta(script):
    texto = script.lower()
    score, notas = 0, []
    cta_words = ["comenta", "comentarios", "sígueme", "comparte", "link", "cavz", "dímelo", "dime"]
    encontrados = [w for w in cta_words if w in texto]
    if encontrados:
        score = 15
        notas.append(("✅", f"CTA presente: *{', '.join(encontrados)}*"))
    else:
        notas.append(("❌", "Sin llamado a la acción — tus virales casi siempre terminan con CTA"))
        notas.append(("💡", "Agrega al final: *'Comenta CAVZ'* / *'Sígueme si eres un despierto'*"))
    return score, notas

def similares(script, rows):
    palabras = set(re.findall(r"[a-záéíóúñ]{4,}", script.lower()))
    resultados = []
    for r in rows:
        if not r["_transcript"]:
            continue
        match = len(palabras & set(re.findall(r"[a-záéíóúñ]{4,}", r["_transcript"].lower())))
        if match >= 3:
            resultados.append((match, r))
    return sorted(resultados, key=lambda x: x[0], reverse=True)[:3]

def render_notas(notas):
    for icon, texto in notas:
        st.markdown(f"{icon} {texto}")

# ── Session state ────────────────────────────────────────
if "script" not in st.session_state:
    st.session_state.script = ""
if "duracion" not in st.session_state:
    st.session_state.duracion = 0
if "analizado" not in st.session_state:
    st.session_state.analizado = False

# ── UI ───────────────────────────────────────────────────
st.markdown("""
<div class="brand-header">
    <span class="brand-cross">†</span>
    <span class="brand-name">Tribu · Leo Cavz</span>
</div>
<h1>Simulador de Reels</h1>
""", unsafe_allow_html=True)
st.caption("Análisis basado en 194 reels · 191 transcripts · saves, shares y retención reales")
st.divider()

script = st.text_area(
    "Script del reel",
    height=280,
    placeholder="Pega aquí lo que vas a decir en tu reel (el script hablado)...",
    label_visibility="visible",
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

if st.session_state.analizado and st.session_state.script.strip():
    script = st.session_state.script
    duracion = st.session_state.duracion
    rows = cargar_datos()
    con_transcript = sum(1 for r in rows if r["_transcript"])

    s_hook, n_hook = score_hook(script)
    s_tema, n_tema = score_tema(script)
    s_dur, n_dur = score_duracion(duracion)
    s_cta, n_cta = score_cta(script)

    total = s_hook + s_tema + s_dur + s_cta
    pct = int((total / 90) * 100)
    pct = min(pct, 100)

    if pct >= 75:
        color = "🔥"
        veredicto = "ALTO POTENCIAL — listo para grabar"
    elif pct >= 50:
        color = "⚡"
        veredicto = "POTENCIAL MEDIO — ajusta los puntos débiles"
    else:
        color = "🚫"
        veredicto = "BAJO POTENCIAL — reescribe el hook"

    st.divider()

    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric("Score", f"{pct}/100")
    with col2:
        st.markdown(f"### {color} {veredicto}")
        st.caption(f"Análisis basado en {con_transcript} transcripts reales")

    st.progress(pct / 100)
    st.divider()

    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("🎯 Hook")
        render_notas(n_hook)
        st.subheader("📣 CTA")
        render_notas(n_cta)
    with col_b:
        st.subheader("🔥 Tema")
        render_notas(n_tema)
        st.subheader("⏱ Duración")
        render_notas(n_dur)

    # ── Sugerencias de mejora ────────────────────────────
    st.divider()
    st.subheader("💡 Cómo mejorar este script")

    sugerencias = []

    # Hook
    primera = script.strip().split("\n")[0].lower()
    tiene_hook_viral = any(re.search(p, primera) for p, _, _ in HOOK_PATRONES)
    if not tiene_hook_viral:
        tema_detectado = next((p for p in PALABRAS_VIRALES if p in script.lower()), "el tema")
        sugerencias.append((
            "🎯 Reescribe el hook",
            f"Tu primera línea no engancha. Prueba alguno de estos formatos que te han funcionado:\n\n"
            f"- *\"En los últimos [X meses/días], [algo que te pasó relacionado con {tema_detectado}]...\"*\n"
            f"- *\"Hablemos de {tema_detectado} — y por qué la mayoría lo está haciendo mal.\"*\n"
            f"- *\"¿Es posible [promesa concreta relacionada con {tema_detectado}]? Sí, y aquí te explico cómo.\"*"
        ))

    # Tema
    temas_presentes = [p for p in PALABRAS_VIRALES if p in script.lower()]
    if not temas_presentes:
        sugerencias.append((
            "🔥 Conecta con un tema de alto impacto",
            "Tu script no menciona ninguno de tus temas más virales. Intenta anclar el mensaje a:\n\n"
            "- **Dinero / hacerse millonario** — siempre funciona en tu audiencia\n"
            "- **Disciplina / proceso** — Monk Mode, Winter Arc, mentalidad\n"
            "- **Crítica al sistema** — universidad, cursos caros, estafas\n\n"
            "No tienes que cambiar el tema, solo conectarlo explícitamente en el script."
        ))

    # CTA
    if s_cta == 0:
        sugerencias.append((
            "📣 Añade un llamado a la acción",
            "Tus reels virales casi siempre terminan con un CTA hablado. Por ejemplo:\n\n"
            "- *\"Comenta CAVZ si quieres el video completo.\"*\n"
            "- *\"Sígueme si eres un despierto.\"*\n"
            "- *\"¿Estás de acuerdo? Dímelo en los comentarios.\"*"
        ))

    # Duración
    if duracion > 70:
        sugerencias.append((
            "⏱ Recorta la duración",
            f"Con {duracion} seg estás fuera de tu zona óptima (30-55 seg). Identifica qué parte del script "
            f"puedes eliminar sin perder el mensaje central. Tus reels más virales van directo al punto."
        ))

    if not sugerencias:
        st.success("✅ El script está bien estructurado. Solo grábalo y publícalo.")
    else:
        for titulo, detalle in sugerencias:
            with st.expander(titulo):
                st.markdown(detalle)

    # ── Reescritura con Claude ───────────────────────────
    st.divider()
    st.subheader("✍️ Reescribir con IA")

    if st.button("Reescribir este script", use_container_width=True):
        feedback_texto = "\n".join(
            f"- {t}: {d}" for t, d in sugerencias
        ) if sugerencias else "El script ya tiene buena estructura."

        top3_ejemplos = "\n\n".join(
            f"Reel con {r['_views']:,} views ({r['_save_rate']:.1f}% saves, {r['_share_rate']:.1f}% shares):\n{r['_transcript'][:350]}"
            for _, r in (similares(script, rows) or [])[:3]
            if r["_transcript"]
        )

        prompt = f"""Eres el asistente de contenido de Leo Cavz, creador mexicano con 557k seguidores en Instagram.
Su estilo es directo, coloquial, provocador y usa lenguaje mexicano auténtico (wey, pendejo, pinche, etc.).

Sus patrones más virales extraídos de transcripts reales:
- Hook más poderoso: "En los últimos X meses/días..." (611k views)
- También funciona: "Hablemos de [tema]...", "¿Es posible...?", "Una de las cosas que nunca voy a entender..."
- Duración óptima en palabras: aprox. 120-200 palabras para 30-55 segundos
- Siempre termina con CTA hablado: "Comenta CAVZ", "Sígueme si eres un despierto", "Dímelo en los comentarios"
- Temas que más conectan: dinero, disciplina, negocios, crítica al sistema, proceso personal
- Save rate objetivo: >2.76% | Share rate objetivo: >1.13% | Retención objetivo: >17 seg

Transcripts de reels similares con buen rendimiento:
{top3_ejemplos if top3_ejemplos else "No encontré reels similares en la base de datos."}

Script original:
{script}

Feedback del análisis:
{feedback_texto}

Reescribe el script hablado aplicando el feedback. Mantén el mismo mensaje central pero mejora:
1. El hook (primera línea debe enganchar en 2 segundos)
2. El ritmo y fluidez para una duración de 30-55 seg
3. El llamado a la acción hablado al final
4. El tono auténtico de Leo — directo, sin rodeos, lenguaje mexicano natural

Devuelve SOLO el script reescrito, como si fuera lo que Leo va a decir frente a la cámara. Sin explicaciones."""

        with st.spinner("Reescribiendo..."):
            try:
                client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
                response = client.messages.create(
                    model="claude-haiku-4-5-20251001",
                    max_tokens=1024,
                    messages=[{"role": "user", "content": prompt}]
                )
                reescrito = response.content[0].text
                st.markdown("**Script reescrito:**")
                st.markdown(f"""
                <div style="background:#111;border-left:2px solid #fff;padding:1.2rem;border-radius:2px;
                font-family:'Barlow',sans-serif;color:#e0e0e0;line-height:1.7;white-space:pre-wrap">{reescrito}</div>
                """, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error: {e}")

    sim = similares(script, rows)
    if sim:
        st.divider()
        st.subheader("Reels tuyos más similares")
        for _, r in sim:
            hook = r["_transcript"][:120]
            save_str = f"{r['_save_rate']:.1f}% saves" if r["_save_rate"] else ""
            share_str = f"{r['_share_rate']:.1f}% shares" if r["_share_rate"] else ""
            watch_str = f"{r['_avg_watch']:.0f}s retención" if r["_avg_watch"] else ""
            metrics = " · ".join(filter(None, [save_str, share_str, watch_str]))
            st.markdown(f"""
            <div class="reel-card">
                <span class="reel-views">{int(r['_views']):,} views</span>
                <span style="color:#666;font-size:0.8rem;margin-left:8px">{metrics}</span><br>
                <span style="color:#555;font-size:0.85rem">{hook}…</span>
            </div>
            """, unsafe_allow_html=True)
