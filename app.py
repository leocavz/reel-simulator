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

PALABRAS_VIRALES = {
    # Alto save rate (>5%) — contenido que la gente guarda
    "estoicismo": 10, "brian tracy": 10, "mamón": 9, "proceso": 9,
    "libro": 9, "conocimiento": 9, "iman gadzhi": 9, "estafa": 8,
    # Alto share rate — contenido que se comparte
    "millonario": 9, "dinero": 9, "negocios": 8, "curso": 8,
    "universidad": 8, "bancarrota": 8, "marketing": 8,
    # Alto volumen en transcripts virales
    "vida": 7, "quieres": 7, "despierto": 8, "dólares": 8,
    "negocio": 7, "disciplina": 8, "banco": 7, "manifestar": 7,
    "monk mode": 9, "winter arc": 8, "novia": 6, "sígueme": 6,
    "pendejo": 5, "verga": 4, "wey": 4, "pinche": 4,
}

HOOK_PATRONES = [
    (r"en los últimos", 15, "historia personal de inicio"),
    (r"hablemos de", 12, "intro directa al tema"),
    (r"¿es posible", 12, "pregunta retórica"),
    (r"una de las cosas que", 10, "observación provocadora"),
    (r"solo los pendejos", 10, "confrontacional"),
    (r"hace \w+ (año|mes|semana)", 10, "historia con tiempo específico"),
    (r"¿sabes (lo que|qué|cuánto)", 10, "pregunta directa al espectador"),
]

TOP_HASHTAGS = [
    "#motivacion", "#negocios", "#podcast", "#crecimientopersonal",
    "#viral", "#dinero", "#disciplina", "#saludmental", "#transformacion",
    "#despiertospodcast", "#dios",
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
            notas.append(("✅", f"Hook tipo *{nombre}* — muy efectivo en tus virales"))
            break
    if not notas:
        if "?" in primera:
            score += 6
            notas.append(("⚠️", "Pregunta en el hook — funciona pero no es tu patrón más fuerte"))
        else:
            notas.append(("❌", "El hook no coincide con tus patrones virales"))
            notas.append(("💡", "Prueba: *'En los últimos X...'* / *'Hablemos de...'* / *'¿Es posible...?'*"))
    if re.search(r"❌.*❌", script.strip().split("\n")[0]):
        score += 10
        notas.append(("✅", "Formato ❌ TITULO ❌ en caption"))
    return min(score, 25), notas

def score_tema(script):
    texto = script.lower()
    score, temas = 0, []
    for palabra, peso in PALABRAS_VIRALES.items():
        if palabra in texto:
            score += peso
            temas.append(palabra)
    score = min(score, 30)
    notas = []
    if temas:
        notas.append(("✅", f"Temas virales detectados: *{', '.join(temas[:6])}*"))
    else:
        notas.append(("⚠️", "No detecté temas de alto rendimiento"))
        notas.append(("💡", "Tus temas más fuertes: dinero, disciplina, negocios, vida, proceso"))
    return score, notas

def score_hashtags(script):
    tags = re.findall(r"#\w+", script.lower())
    buenos = [t for t in tags if t in TOP_HASHTAGS]
    score, notas = 0, []
    if buenos:
        score += min(len(buenos) * 5, 15)
        notas.append(("✅", f"Hashtags que te funcionan: *{', '.join(buenos)}*"))
    else:
        notas.append(("⚠️", "Sin hashtags probados — agrega: #motivacion #negocios #podcast"))
    if 3 <= len(tags) <= 6:
        score += 5
        notas.append(("✅", "Cantidad de hashtags ideal (3-6)"))
    elif len(tags) > 6:
        notas.append(("⚠️", "Demasiados hashtags — tus virales usan 3-5 máximo"))
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

def similares(script, rows):
    palabras = set(re.findall(r"[a-záéíóúñ]{4,}", script.lower()))
    resultados = []
    for r in rows:
        fuente = r["_transcript"] or r["caption"]
        match = len(palabras & set(re.findall(r"[a-záéíóúñ]{4,}", fuente.lower())))
        if match >= 3:
            resultados.append((match, r))
    return sorted(resultados, key=lambda x: x[0], reverse=True)[:3]

def render_notas(notas):
    for icon, texto in notas:
        st.markdown(f"{icon} {texto}")

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
    placeholder="Pega aquí el script o caption de tu reel...",
    label_visibility="visible",
)

st.markdown("<br>", unsafe_allow_html=True)
duracion = st.slider("Duración estimada (segundos)", 0, 120, 0, step=5,
                     help="Pon 0 si no sabes aún")
st.markdown("<br>", unsafe_allow_html=True)

analizar = st.button("Analizar reel", type="primary", use_container_width=True)

if analizar and script.strip():
    rows = cargar_datos()
    con_transcript = sum(1 for r in rows if r["_transcript"])

    s_hook, n_hook = score_hook(script)
    s_tema, n_tema = score_tema(script)
    s_tags, n_tags = score_hashtags(script)
    s_dur, n_dur = score_duracion(duracion)

    total = s_hook + s_tema + s_tags + s_dur
    pct = int((total / 85) * 100)

    if pct >= 75:
        color = "🔥"
        veredicto = "ALTO POTENCIAL — listo para grabar"
        bg = "success"
    elif pct >= 50:
        color = "⚡"
        veredicto = "POTENCIAL MEDIO — ajusta los puntos débiles"
        bg = "warning"
    else:
        color = "🚫"
        veredicto = "BAJO POTENCIAL — reescribe el hook"
        bg = "error"

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
        st.subheader("💬 Hashtags")
        render_notas(n_tags)
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
            "- **Crítica al sistema** — universidad, cursos caros, política\n\n"
            "No tienes que cambiar el tema, solo conectarlo explícitamente."
        ))

    # Hashtags
    tags = re.findall(r"#\w+", script.lower())
    buenos_tags = [t for t in tags if t in TOP_HASHTAGS]
    if not buenos_tags:
        sugerencias.append((
            "💬 Agrega hashtags probados",
            "Ninguno de tus hashtags actuales aparece en tus reels virales. Al final del caption agrega:\n\n"
            "`#motivacion #negocios #podcast #crecimientopersonal`"
        ))

    # Duración
    if duracion > 70:
        sugerencias.append((
            "⏱ Recorta la duración",
            f"Con {duracion} seg estás fuera de tu zona óptima (30-55 seg). Identifica qué parte del script "
            f"puedes eliminar sin perder el mensaje central. Tus reels más virales van directo al punto."
        ))

    # CTA
    if not any(w in script.lower() for w in ["comenta", "comentarios", "sígueme", "comparte", "link", "cavz"]):
        sugerencias.append((
            "📣 Añade un llamado a la acción",
            "Tus reels virales casi siempre terminan con un CTA. Por ejemplo:\n\n"
            "- *\"Comenta CAVZ si quieres el video completo.\"*\n"
            "- *\"Sígueme si eres un despierto.\"*\n"
            "- *\"¿Estás de acuerdo? Dímelo en los comentarios.\"*"
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
            f"Reel con {r['_views']:,} views ({r['_save_rate']:.1f}% saves):\n{(r['_transcript'] or r['caption'])[:300]}"
            for _, r in (similares(script, rows) or [])[:3]
        )

        prompt = f"""Eres el asistente de contenido de Leo Cavz, creador mexicano con 557k seguidores en Instagram.
Su estilo es directo, coloquial, provocador y usa lenguaje mexicano auténtico.

Sus patrones más virales:
- Hook: ❌ TITULO EN MAYÚSCULAS ❌
- Duración óptima: 30-55 segundos
- Temas que pegan: dinero, disciplina, negocios, estoicismo, proceso, millonario
- Save rate objetivo: >2.76% | Share rate objetivo: >1.13% | Retención objetivo: >17 seg

Reels similares de referencia con buen rendimiento:
{top3_ejemplos}

Script original:
{script}

Feedback del análisis:
{feedback_texto}

Reescribe el script aplicando el feedback. Mantén el mismo mensaje central pero mejora:
1. El hook (primera línea debe enganchar en 2 segundos)
2. El ritmo y fluidez para una duración de 30-55 seg
3. El llamado a la acción al final
4. El tono auténtico de Leo

Devuelve SOLO el script reescrito, sin explicaciones."""

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
            fuente = "transcript" if r["_transcript"] else "caption"
            hook = (r["_transcript"] or r["caption"])[:100]
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

elif analizar and not script.strip():
    st.warning("Pega un script antes de analizar.")
