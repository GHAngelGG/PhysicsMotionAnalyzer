"""
Genera un PowerPoint corto de 4 slides para la exposición del proyecto.
Incluye el QR del sitio web para que la audiencia lo escanee al final.
"""
import os
import sys
import qrcode
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN

# Forzar UTF-8 en stdout para Windows
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJ_DIR = os.path.dirname(OUT_DIR)
URL = "https://ghangelgg.github.io/PhysicsMotionAnalyzer/"
REPO = "https://github.com/GHAngelGG/PhysicsMotionAnalyzer"

# ─── 1. Generar QR ───
print("[1/2] Generando QR…")
qr_path = os.path.join(OUT_DIR, "qr_sitio.png")
qr = qrcode.QRCode(
    version=1, error_correction=qrcode.constants.ERROR_CORRECT_H,
    box_size=12, border=2,
)
qr.add_data(URL)
qr.make(fit=True)
img = qr.make_image(fill_color="#0f172a", back_color="white")
img.save(qr_path)
print(f"   ✓ QR guardado: {qr_path}")

# ─── 2. Crear PPT ───
print("\n[2/2] Creando PowerPoint…")
prs = Presentation()
prs.slide_width = Inches(13.33)   # 16:9
prs.slide_height = Inches(7.5)

# Colores
AZUL_OSCURO = RGBColor(0x0F, 0x17, 0x2A)
AZUL        = RGBColor(0x25, 0x63, 0xEB)
AZUL_CLARO  = RGBColor(0xDB, 0xEA, 0xFE)
VERDE       = RGBColor(0x10, 0xB9, 0x81)
NARANJA     = RGBColor(0xF5, 0x9E, 0x0B)
PURPURA     = RGBColor(0x8B, 0x5C, 0xF6)
ROJO        = RGBColor(0xEF, 0x44, 0x44)
BLANCO      = RGBColor(0xFF, 0xFF, 0xFF)
GRIS        = RGBColor(0x64, 0x74, 0x8B)
GRIS_LUZ    = RGBColor(0xCB, 0xD5, 0xE1)


def fondo_solido(slide, color):
    bg = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height
    )
    bg.fill.solid()
    bg.fill.fore_color.rgb = color
    bg.line.fill.background()
    bg.shadow.inherit = False
    return bg


def text_box(slide, x, y, w, h, text, size=18, bold=False,
             color=BLANCO, align=PP_ALIGN.LEFT, font="Segoe UI"):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0.05)
    tf.margin_top = tf.margin_bottom = Inches(0.05)
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.name = font
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    return tb


def add_accent_bar(slide, x, y, w, h, color):
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, h)
    bar.fill.solid(); bar.fill.fore_color.rgb = color
    bar.line.fill.background(); bar.shadow.inherit = False
    return bar


# ════════════════════════════════════════════════════════
# SLIDE 1 — PORTADA
# ════════════════════════════════════════════════════════
slide = prs.slides.add_slide(prs.slide_layouts[6])  # blank
fondo_solido(slide, AZUL_OSCURO)
# Acento lateral
add_accent_bar(slide, 0, 0, Inches(0.15), prs.slide_height, AZUL)
# Logo emoji + título
text_box(slide, Inches(1.0), Inches(2.0), Inches(11), Inches(0.6),
         "PROYECTO FINAL · FÍSICA I", size=14, bold=True, color=GRIS_LUZ)
text_box(slide, Inches(1.0), Inches(2.5), Inches(11), Inches(1.2),
         "PhysicsMotionAnalyzer", size=54, bold=True, color=BLANCO)
text_box(slide, Inches(1.0), Inches(3.6), Inches(11), Inches(0.7),
         "Sistema Inteligente de Análisis Cinemático en Tiempo Real",
         size=22, color=AZUL_CLARO)
# Línea divisora
linea = slide.shapes.add_shape(
    MSO_SHAPE.RECTANGLE, Inches(1.0), Inches(4.5),
    Inches(2.5), Emu(28000),
)
linea.fill.solid(); linea.fill.fore_color.rgb = VERDE
linea.line.fill.background(); linea.shadow.inherit = False
# Datos
text_box(slide, Inches(1.0), Inches(4.8), Inches(11), Inches(0.5),
         "Universidad Mariano Gálvez de Guatemala",
         size=16, color=GRIS_LUZ)
text_box(slide, Inches(1.0), Inches(5.3), Inches(11), Inches(0.5),
         "Facultad de Ingeniería en Sistemas",
         size=14, color=GRIS)
# Tecnologías badges
text_box(slide, Inches(1.0), Inches(6.3), Inches(11), Inches(0.5),
         "Python 3.14   ·   OpenCV   ·   NumPy   ·   GitHub Pages",
         size=11, color=GRIS, font="Consolas")


# ════════════════════════════════════════════════════════
# SLIDE 2 — EL PROBLEMA Y LA SOLUCIÓN
# ════════════════════════════════════════════════════════
slide = prs.slides.add_slide(prs.slide_layouts[6])
fondo_solido(slide, BLANCO)
add_accent_bar(slide, 0, 0, prs.slide_width, Inches(0.7), AZUL_OSCURO)
text_box(slide, Inches(0.5), Inches(0.15), Inches(12), Inches(0.45),
         "¿QUÉ HACE EL SISTEMA?",
         size=18, bold=True, color=BLANCO)

# Subtítulo
text_box(slide, Inches(0.6), Inches(1.0), Inches(12), Inches(0.6),
         "Mide cinemática con solo una cámara, sin sensores costosos",
         size=22, bold=True, color=AZUL_OSCURO)

# 3 tarjetas: Detecta · Calcula · Clasifica
def tarjeta(x, y, w, h, icono, titulo, desc, color):
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h)
    card.fill.solid(); card.fill.fore_color.rgb = RGBColor(0xF8, 0xFA, 0xFC)
    card.line.color.rgb = RGBColor(0xE2, 0xE8, 0xF0)
    card.line.width = Pt(0.75)
    card.shadow.inherit = False
    # Barra superior de color
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, Inches(0.12))
    bar.fill.solid(); bar.fill.fore_color.rgb = color
    bar.line.fill.background(); bar.shadow.inherit = False
    # Icono
    text_box(slide, x, y + Inches(0.3), w, Inches(0.8),
             icono, size=42, color=color, align=PP_ALIGN.CENTER)
    # Título
    text_box(slide, x, y + Inches(1.3), w, Inches(0.5),
             titulo, size=18, bold=True, color=AZUL_OSCURO, align=PP_ALIGN.CENTER)
    # Descripción
    text_box(slide, x + Inches(0.2), y + Inches(1.9), w - Inches(0.4), Inches(1.5),
             desc, size=12, color=GRIS, align=PP_ALIGN.CENTER)


tarjeta(Inches(0.7),  Inches(2.0), Inches(3.9), Inches(3.8),
        "🎯", "DETECTA",
        "Localiza un objeto por su color usando visión por computadora (HSV) "
        "y lo sigue específicamente, ignorando otros objetos del mismo color.",
        AZUL)
tarjeta(Inches(4.75), Inches(2.0), Inches(3.9), Inches(3.8),
        "📐", "CALCULA",
        "Mide posición, velocidad y aceleración en tiempo real "
        "usando diferencias finitas y filtros para reducir ruido.",
        VERDE)
tarjeta(Inches(8.8),  Inches(2.0), Inches(3.9), Inches(3.8),
        "✓", "CLASIFICA",
        "Identifica automáticamente si el movimiento es MRU, MRUV "
        "o Caída Libre, y compara contra la curva teórica.",
        NARANJA)

# Pie de slide
text_box(slide, Inches(0.6), Inches(6.4), Inches(12), Inches(0.5),
         "👉  Vamos a verlo en vivo…",
         size=18, bold=True, color=AZUL, align=PP_ALIGN.CENTER)


# ════════════════════════════════════════════════════════
# SLIDE 3 — RESULTADOS Y VALIDACIÓN
# ════════════════════════════════════════════════════════
slide = prs.slides.add_slide(prs.slide_layouts[6])
fondo_solido(slide, BLANCO)
add_accent_bar(slide, 0, 0, prs.slide_width, Inches(0.7), AZUL_OSCURO)
text_box(slide, Inches(0.5), Inches(0.15), Inches(12), Inches(0.45),
         "RESULTADOS Y VALIDACIÓN",
         size=18, bold=True, color=BLANCO)
text_box(slide, Inches(0.6), Inches(1.0), Inches(12), Inches(0.6),
         "Precisión medida contra valores teóricos",
         size=20, bold=True, color=AZUL_OSCURO)

# Tabla de resultados (4 columnas: tipo, teórico, medido, error)
def fila_kpi(x, y, w, color, titulo_es, valor_principal, unidad, sub):
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                                  x, y, w, Inches(1.7))
    card.fill.solid(); card.fill.fore_color.rgb = RGBColor(0xF8, 0xFA, 0xFC)
    card.line.color.rgb = RGBColor(0xE2, 0xE8, 0xF0)
    card.line.width = Pt(0.75); card.shadow.inherit = False
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,
                                 x, y, Inches(0.1), Inches(1.7))
    bar.fill.solid(); bar.fill.fore_color.rgb = color
    bar.line.fill.background(); bar.shadow.inherit = False
    text_box(slide, x + Inches(0.3), y + Inches(0.15), w - Inches(0.3), Inches(0.4),
             titulo_es, size=11, bold=True, color=GRIS)
    text_box(slide, x + Inches(0.3), y + Inches(0.55), w - Inches(0.3), Inches(0.7),
             f"{valor_principal} {unidad}", size=24, bold=True, color=color)
    text_box(slide, x + Inches(0.3), y + Inches(1.25), w - Inches(0.3), Inches(0.4),
             sub, size=10, color=GRIS)


fila_kpi(Inches(0.6),  Inches(1.9), Inches(3.0), AZUL,
         "MRU", "0.00", "%", "Velocidad constante · error medio")
fila_kpi(Inches(3.8),  Inches(1.9), Inches(3.0), VERDE,
         "MRUV", "0.70", "%", "Aceleración constante · error medio")
fila_kpi(Inches(7.0),  Inches(1.9), Inches(3.0), NARANJA,
         "CAÍDA LIBRE", "4.54", "%", "g medido vs 9.8 m/s²")
fila_kpi(Inches(10.2), Inches(1.9), Inches(2.6), PURPURA,
         "DETECCIONES", "86", "pts", "Frames procesados con éxito")

# Bullets clave
text_box(slide, Inches(0.6), Inches(4.0), Inches(12), Inches(0.5),
         "Cómo lo logramos",
         size=18, bold=True, color=AZUL_OSCURO)
bullets = [
    ("●", "Calibrador visual con lock-on que sigue el objeto sin distraerse"),
    ("●", "Filtro Savitzky-Golay que suaviza el ruido de las derivadas"),
    ("●", "Recorte del video al tramo de movimiento puro"),
    ("●", "Comparación automática contra ecuaciones teóricas de cinemática"),
]
for i, (b, t) in enumerate(bullets):
    y_pos = Inches(4.7 + i * 0.5)
    text_box(slide, Inches(0.8), y_pos, Inches(0.3), Inches(0.4),
             b, size=14, color=AZUL)
    text_box(slide, Inches(1.2), y_pos, Inches(11), Inches(0.4),
             t, size=14, color=AZUL_OSCURO)


# ════════════════════════════════════════════════════════
# SLIDE 4 — QR + CIERRE
# ════════════════════════════════════════════════════════
slide = prs.slides.add_slide(prs.slide_layouts[6])
fondo_solido(slide, AZUL_OSCURO)
add_accent_bar(slide, 0, 0, Inches(0.15), prs.slide_height, AZUL)

# Título
text_box(slide, Inches(0.7), Inches(0.5), Inches(12), Inches(0.7),
         "PROBALO AHORA  ·  ESCANEÁ EL QR",
         size=30, bold=True, color=BLANCO, align=PP_ALIGN.CENTER)
text_box(slide, Inches(0.7), Inches(1.3), Inches(12), Inches(0.5),
         "Funciona desde celular y PC, sin necesidad de instalar nada",
         size=16, color=AZUL_CLARO, align=PP_ALIGN.CENTER)

# QR (centrado)
qr_w = Inches(3.8)
qr_h = Inches(3.8)
qr_x = (prs.slide_width - qr_w) // 2
qr_y = Inches(2.1)
# Fondo blanco para el QR
qr_bg = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                                qr_x - Inches(0.15), qr_y - Inches(0.15),
                                qr_w + Inches(0.3), qr_h + Inches(0.3))
qr_bg.fill.solid(); qr_bg.fill.fore_color.rgb = BLANCO
qr_bg.line.fill.background(); qr_bg.shadow.inherit = False
slide.shapes.add_picture(qr_path, qr_x, qr_y, qr_w, qr_h)

# URL debajo
text_box(slide, Inches(0.7), Inches(6.2), Inches(12), Inches(0.4),
         URL, size=14, color=AZUL_CLARO,
         align=PP_ALIGN.CENTER, font="Consolas")

# Links de referencia abajo
text_box(slide, Inches(0.7), Inches(6.7), Inches(12), Inches(0.4),
         f"Código fuente:  {REPO}",
         size=10, color=GRIS, align=PP_ALIGN.CENTER, font="Consolas")

# Gracias
text_box(slide, Inches(0.7), Inches(7.05), Inches(12), Inches(0.4),
         "¡ GRACIAS !",
         size=14, bold=True, color=VERDE, align=PP_ALIGN.CENTER)

# Guardar
out_path = os.path.join(PROJ_DIR, "informe", "Exposicion_PhysicsMotionAnalyzer.pptx")
prs.save(out_path)
print(f"   ✓ PPT guardado: {out_path}")

print("\n" + "=" * 60)
print("LISTO. El PowerPoint tiene 4 slides:")
print("  1. Portada con título y datos del proyecto")
print("  2. ¿Qué hace? (3 tarjetas: Detecta, Calcula, Clasifica)")
print("  3. Resultados (4 KPIs: MRU, MRUV, Caída Libre, Detecciones)")
print("  4. QR + URL para escanear (cierre)")
print("=" * 60)
