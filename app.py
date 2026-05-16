import streamlit as st
import csv
import re
from pathlib import Path
from collections import Counter

# ── Config ──────────────────────────────────────────────
st.set_page_config(
    page_title="Simulador de Reels · Leo Cavz",
    page_icon="🎬",
    layout="centered",
)

BASE = Path(__file__).parent
CSV_FILE = BASE / "leo_cavz_reels.csv"
TRANSCRIPTS_DIR = BASE / "transcripts"

PALABRAS_VIRALES = {
    "vida": 8, "quieres": 8, "despierto": 9, "dólares": 8, "dinero": 8,
    "comentarios": 6, "negocios": 8, "libro": 7, "proceso": 7, "novia": 6,
    "disciplina": 8, "millonario": 9, "universidad": 7, "curso": 6,
    "monk mode": 9, "winter arc": 8, "manifestar": 7, "banco": 7,
    "bancarrota": 8, "marketing": 7, "pinche": 5, "pendejo": 6,
    "verga": 4, "wey": 4, "chingados": 5,
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
        try:
            r["_views"] = int(r["views"])
        except:
            r["_views"] = 0
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
    return sorted(resultados, reverse=True)[:3]

def render_notas(notas):
    for icon, texto in notas:
        st.markdown(f"{icon} {texto}")

# ── UI ───────────────────────────────────────────────────
st.title("🎬 Simulador de Reels")
st.caption("Basado en el análisis de tus 194 reels y 30 transcripts reales · Leo Cavz")
st.divider()

script = st.text_area(
    "Pega tu script aquí",
    height=280,
    placeholder="Escribe o pega el script de tu reel...",
)

duracion = st.slider("Duración estimada del reel (segundos)", 0, 120, 0, step=5,
                     help="Pon 0 si no sabes aún")

analizar = st.button("🔍 Analizar reel", type="primary", use_container_width=True)

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

    sim = similares(script, rows)
    if sim:
        st.divider()
        st.subheader("📊 Tus reels más similares")
        for _, r in sim:
            fuente = "transcript" if r["_transcript"] else "caption"
            hook = (r["_transcript"] or r["caption"])[:100]
            st.markdown(f"**{int(r['_views']):,} views** · `{fuente}` · {hook}…")

elif analizar and not script.strip():
    st.warning("Pega un script antes de analizar.")
