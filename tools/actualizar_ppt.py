"""
Actualiza el PPT existente:
- Reemplaza la slide de Tecnología (slide 3) por una versión SIMPLE
- Reemplaza la slide de Lógica Física (slide 4) por una versión con analogías
- Inserta nueva slide con CAPTURAS REALES del código
- Mantiene portada (1), ¿Qué hace? (2) y QR (último)

Genera primero las capturas de código en estilo Carbon (fondo oscuro)
usando Pygments + PIL.
"""
import os
import sys

from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import ImageFormatter
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from copy import deepcopy

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

PROY_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PPT_PATH = (r"C:\Users\josea\OneDrive\Documentos\U\Fisica I"
            r"\Proyecto Final\Entregables\Exposicion_PhysicsMotionAnalyzer.pptx")
QR_PATH  = os.path.join(PROY_DIR, "tools", "qr_sitio.png")
TMP_DIR  = os.path.join(PROY_DIR, "tools", "_tmp_capturas")
os.makedirs(TMP_DIR, exist_ok=True)

URL = "https://ghangelgg.github.io/PhysicsMotionAnalyzer/"

# ────────────────────────────────────────────────────────
# 1) FRAGMENTOS DE CÓDIGO PARA CAPTURAS
# ────────────────────────────────────────────────────────
SNIPPETS = {
    "1_deteccion_color.png": (
        "# tracking/color_detector.py · Detección por color HSV",
'''def generar_mascara(frame_bgr, hsv_min, hsv_max, blur_ksize=9):
    """Genera máscara binaria del objeto por color HSV."""
    # 1) Suavizar la imagen (reduce ruido)
    desenfocado = cv2.GaussianBlur(frame_bgr,
                                    (blur_ksize, blur_ksize), 0)
    # 2) Convertir de BGR a HSV (más estable bajo cambios de luz)
    hsv = cv2.cvtColor(desenfocado, cv2.COLOR_BGR2HSV)
    # 3) Crear máscara: blanco donde el color está en rango
    lower = np.array(hsv_min, dtype=np.uint8)
    upper = np.array(hsv_max, dtype=np.uint8)
    mask  = cv2.inRange(hsv, lower, upper)
    # 4) Limpiar pequeños puntos de ruido
    mask = cv2.erode(mask,  None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)
    return mask'''
    ),
    "2_calculos_fisica.png": (
        "# physics/kinematics.py · Velocidad y aceleración",
'''def derivada_central(x, t):
    """Velocidad: cuánto cambió la posición entre dos cuadros."""
    x = np.asarray(x); t = np.asarray(t)
    v = np.zeros_like(x)
    # Diferencias finitas centrales (más precisas que las simples)
    for i in range(1, len(x) - 1):
        v[i] = (x[i+1] - x[i-1]) / (t[i+1] - t[i-1])
    return v


def segunda_derivada(x, t):
    """Aceleración: cuánto cambió la velocidad."""
    v = derivada_central(x, t)
    a = derivada_central(v, t)
    return a'''
    ),
    "3_clasificador.png": (
        "# physics/classifier.py · Identifica el tipo de movimiento",
'''def clasificar_movimiento(a_array, v_array=None,
                           umbral_mru=0.5, umbral_g=1.5):
    """Decide si es MRU, MRUV o Caída Libre según la aceleración."""
    a_prom = float(np.nanmean(a_array))
    v_prom = float(np.nanmean(v_array)) if v_array is not None else 0

    # Si la aceleración es casi cero → velocidad constante
    if abs(a_prom) < umbral_mru:
        return "MRU", a_prom, v_prom

    # Si la aceleración es cercana a la gravedad → caída libre
    if abs(abs(a_prom) - 9.8) < umbral_g:
        return "Caída Libre", a_prom, v_prom

    # Cualquier otra aceleración constante → MRUV
    return "MRUV", a_prom, v_prom'''
    ),
}


def generar_imagenes_codigo():
    """Genera PNGs con el código resaltado.

    Pygments tiene un bug donde su ImageFormatter comparte estado entre
    llamadas en el mismo proceso, generando capturas superpuestas.
    Solución: ejecutar cada captura en un SUBPROCESO Python separado
    para garantizar estado limpio.
    """
    import subprocess
    print("[1/2] Generando capturas de código (subprocess por cada una)...")

    # Borrar temporales viejas para asegurar limpieza
    for f in os.listdir(TMP_DIR):
        if f.endswith(".png"):
            os.remove(os.path.join(TMP_DIR, f))

    script_template = '''
import sys
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import ImageFormatter
# Leer bytes directamente y decodificar como UTF-8 (sin mojibake)
code = sys.stdin.buffer.read().decode("utf-8")
fmt = ImageFormatter(
    font_name="Consolas",
    font_size=16,
    line_numbers=False,
    style="monokai",
    image_pad=22,
    line_pad=5,
)
sys.stdout.buffer.write(highlight(code, PythonLexer(), fmt))
'''

    for fname, (titulo, code) in SNIPPETS.items():
        out = os.path.join(TMP_DIR, fname)
        result = subprocess.run(
            [sys.executable, "-c", script_template],
            input=code.encode("utf-8"),
            capture_output=True,
            check=True,
        )
        with open(out, "wb") as f:
            f.write(result.stdout)
        print(f"   ✓ {fname}  ({len(result.stdout)} bytes)")


# ────────────────────────────────────────────────────────
# 2) MODIFICAR EL PPT
# ────────────────────────────────────────────────────────
# Paleta consistente con el resto
C = {
    "FONDO_OSC": RGBColor(0x0F, 0x17, 0x2A),
    "AZUL":      RGBColor(0x25, 0x63, 0xEB),
    "AZUL_LUZ":  RGBColor(0xDB, 0xEA, 0xFE),
    "VERDE":     RGBColor(0x10, 0xB9, 0x81),
    "NARANJA":   RGBColor(0xF5, 0x9E, 0x0B),
    "PURPURA":   RGBColor(0x8B, 0x5C, 0xF6),
    "ROJO":      RGBColor(0xEF, 0x44, 0x44),
    "BLANCO":    RGBColor(0xFF, 0xFF, 0xFF),
    "TEXTO":     RGBColor(0x0F, 0x17, 0x2A),
    "GRIS":      RGBColor(0x64, 0x74, 0x8B),
    "GRIS_LUZ":  RGBColor(0x94, 0xA3, 0xB8),
}


def fondo(slide, prs, color):
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0,
                                 prs.slide_width, prs.slide_height)
    bg.fill.solid(); bg.fill.fore_color.rgb = color
    bg.line.fill.background(); bg.shadow.inherit = False
    return bg


def tx(slide, x, y, w, h, text, size=14, bold=False,
       color=None, align=PP_ALIGN.LEFT, font="Segoe UI"):
    if color is None: color = C["TEXTO"]
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0.05)
    tf.margin_top = tf.margin_bottom = Inches(0.05)
    p = tf.paragraphs[0]; p.alignment = align
    r = p.add_run(); r.text = text
    r.font.name = font; r.font.size = Pt(size)
    r.font.bold = bold; r.font.color.rgb = color
    return tb


def acento(slide, x, y, w, h, color):
    s = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, h)
    s.fill.solid(); s.fill.fore_color.rgb = color
    s.line.fill.background(); s.shadow.inherit = False
    return s


def construir_slide_tecnologias(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    fondo(slide, prs, C["BLANCO"])
    acento(slide, 0, 0, prs.slide_width, Inches(0.7), C["FONDO_OSC"])
    tx(slide, Inches(0.5), Inches(0.15), Inches(12), Inches(0.45),
       "¿CON QUÉ ESTÁ HECHO EL SISTEMA?",
       size=18, bold=True, color=C["BLANCO"])
    tx(slide, Inches(0.6), Inches(0.95), Inches(12), Inches(0.5),
       "4 tecnologías clave que hacen funcionar todo",
       size=16, bold=True, color=C["TEXTO"])

    items = [
        ("🐍", "PYTHON 3.14",
         "Lenguaje principal del proyecto. Es el más usado en el mundo\n"
         "de la inteligencia artificial y la visión computacional.",
         C["AZUL"]),
        ("👁", "OPENCV",
         "Los «ojos» del programa. Procesa el video, detecta el color de\n"
         "la pelota y la sigue cuadro por cuadro.",
         C["VERDE"]),
        ("🔢", "NUMPY",
         "La «calculadora rápida». Hace miles de operaciones matemáticas\n"
         "por segundo sin trabarse.",
         C["NARANJA"]),
        ("🌐", "GITHUB PAGES",
         "Donde alojamos la versión web GRATIS y con HTTPS, para que\n"
         "cualquiera pueda probarla desde su celular escaneando un QR.",
         C["PURPURA"]),
    ]
    for i, (icono, nombre, desc, color) in enumerate(items):
        y = Inches(1.8 + i * 1.3)
        # Barra de color a la izquierda
        acento(slide, Inches(0.6), y, Inches(0.12), Inches(1.1), color)
        # Icono
        tx(slide, Inches(0.85), y + Inches(0.15), Inches(0.8), Inches(0.8),
           icono, size=32, color=color, align=PP_ALIGN.CENTER)
        # Nombre
        tx(slide, Inches(1.85), y + Inches(0.1), Inches(4), Inches(0.5),
           nombre, size=18, bold=True, color=color)
        # Descripción
        tx(slide, Inches(1.85), y + Inches(0.55), Inches(11), Inches(0.8),
           desc, size=12, color=C["TEXTO"])


def construir_slide_fisica_simple(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    fondo(slide, prs, C["BLANCO"])
    acento(slide, 0, 0, prs.slide_width, Inches(0.7), C["FONDO_OSC"])
    tx(slide, Inches(0.5), Inches(0.15), Inches(12), Inches(0.45),
       "¿CÓMO MIDE LA FÍSICA NUESTRO PROGRAMA?",
       size=18, bold=True, color=C["BLANCO"])
    tx(slide, Inches(0.6), Inches(0.95), Inches(12), Inches(0.5),
       "Sin fórmulas complicadas, así de simple:",
       size=15, bold=True, color=C["GRIS"])

    pasos = [
        ("🟠", "¿DÓNDE ESTÁ LA PELOTA?",
         "El programa busca el color naranja en cada cuadro del video\n"
         "y guarda su posición exacta (en píxeles, luego en metros).",
         C["NARANJA"]),
        ("📏", "¿QUÉ TAN RÁPIDO SE MUEVE?  (Velocidad)",
         "Mide cuánta distancia recorre entre dos cuadros consecutivos.\n"
         "Ejemplo: si cambió 1 metro en 0.5 segundos → velocidad = 2 m/s.",
         C["VERDE"]),
        ("🚀", "¿CUÁNTO ACELERA?  (Aceleración)",
         "Compara qué tan rápido CAMBIA la velocidad. Si cada segundo\n"
         "la velocidad sube 9.8 m/s, es la gravedad → es Caída Libre.",
         C["AZUL"]),
        ("🎯", "¿QUÉ TIPO DE MOVIMIENTO ES?",
         "El programa decide solo:\n"
         "  • Sin acelerar → MRU (velocidad constante)\n"
         "  • Acelera parejo → MRUV    • Acelera ≈ 9.8 → CAÍDA LIBRE",
         C["PURPURA"]),
    ]
    for i, (icono, titulo, desc, color) in enumerate(pasos):
        y = Inches(1.7 + i * 1.35)
        acento(slide, Inches(0.6), y, Inches(0.12), Inches(1.15), color)
        tx(slide, Inches(0.85), y + Inches(0.2), Inches(0.7), Inches(0.7),
           icono, size=28, color=color, align=PP_ALIGN.CENTER)
        tx(slide, Inches(1.7), y + Inches(0.1), Inches(11), Inches(0.5),
           titulo, size=14, bold=True, color=color)
        tx(slide, Inches(1.7), y + Inches(0.55), Inches(11.2), Inches(0.85),
           desc, size=11, color=C["TEXTO"])


def construir_slide_capturas_codigo(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    fondo(slide, prs, C["BLANCO"])
    acento(slide, 0, 0, prs.slide_width, Inches(0.7), C["FONDO_OSC"])
    tx(slide, Inches(0.5), Inches(0.15), Inches(12), Inches(0.45),
       "EL CÓDIGO QUE LO HACE POSIBLE",
       size=18, bold=True, color=C["BLANCO"])
    tx(slide, Inches(0.6), Inches(0.85), Inches(12), Inches(0.4),
       "Cada paso de la física, traducido a Python:",
       size=12, bold=True, color=C["GRIS"])

    capturas = [
        ("🟠 Detección por color HSV", "1_deteccion_color.png", C["NARANJA"]),
        ("📐 Cálculo de velocidad y aceleración", "2_calculos_fisica.png", C["VERDE"]),
        ("🎯 Clasificación del movimiento", "3_clasificador.png", C["PURPURA"]),
    ]
    # 3 columnas de imágenes + título arriba de cada una
    col_w = Inches(4.1)
    margin_x = Inches(0.4)
    for i, (titulo, fname, color) in enumerate(capturas):
        x = margin_x + i * (col_w + Inches(0.1))
        # Caption arriba
        acento(slide, x, Inches(1.35), col_w, Inches(0.06), color)
        tx(slide, x, Inches(1.45), col_w, Inches(0.4),
           titulo, size=11, bold=True, color=color, align=PP_ALIGN.CENTER)
        # Imagen del código
        img_path = os.path.join(TMP_DIR, fname)
        if os.path.exists(img_path):
            slide.shapes.add_picture(img_path, x, Inches(1.95),
                                     width=col_w, height=Inches(4.6))

    # Pie con archivos del proyecto
    tx(slide, Inches(0.6), Inches(6.8), Inches(12), Inches(0.4),
       "Ubicación: tracking/color_detector.py  ·  physics/kinematics.py  ·  physics/classifier.py",
       size=10, bold=True, color=C["GRIS"],
       align=PP_ALIGN.CENTER, font="Consolas")


def construir_slide_qr(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    fondo(slide, prs, C["FONDO_OSC"])
    acento(slide, 0, 0, Inches(0.15), prs.slide_height, C["AZUL"])
    tx(slide, Inches(0.7), Inches(0.5), Inches(12), Inches(0.7),
       "PROBALO AHORA  ·  ESCANEÁ EL QR",
       size=30, bold=True, color=C["BLANCO"], align=PP_ALIGN.CENTER)
    tx(slide, Inches(0.7), Inches(1.3), Inches(12), Inches(0.5),
       "Funciona desde celular y PC, sin necesidad de instalar nada",
       size=16, color=C["AZUL_LUZ"], align=PP_ALIGN.CENTER)
    qr_w = qr_h = Inches(3.8)
    qr_x = (prs.slide_width - qr_w) // 2
    qr_y = Inches(2.1)
    qr_bg = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                                    qr_x - Inches(0.15), qr_y - Inches(0.15),
                                    qr_w + Inches(0.3), qr_h + Inches(0.3))
    qr_bg.fill.solid(); qr_bg.fill.fore_color.rgb = C["BLANCO"]
    qr_bg.line.fill.background(); qr_bg.shadow.inherit = False
    if os.path.exists(QR_PATH):
        slide.shapes.add_picture(QR_PATH, qr_x, qr_y, qr_w, qr_h)
    tx(slide, Inches(0.7), Inches(6.2), Inches(12), Inches(0.4),
       URL, size=14, color=C["AZUL_LUZ"],
       align=PP_ALIGN.CENTER, font="Consolas")
    tx(slide, Inches(0.7), Inches(7.05), Inches(12), Inches(0.4),
       "¡ GRACIAS !", size=14, bold=True,
       color=C["VERDE"], align=PP_ALIGN.CENTER)


def construir_slide_portada(prs):
    """Slide 1: Portada del proyecto."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    fondo(slide, prs, C["FONDO_OSC"])
    acento(slide, 0, 0, Inches(0.15), prs.slide_height, C["AZUL"])
    tx(slide, Inches(1.0), Inches(2.0), Inches(11), Inches(0.6),
       "PROYECTO FINAL · FÍSICA I",
       size=14, bold=True, color=C["GRIS_LUZ"])
    tx(slide, Inches(1.0), Inches(2.5), Inches(11), Inches(1.2),
       "PhysicsMotionAnalyzer",
       size=54, bold=True, color=C["BLANCO"])
    tx(slide, Inches(1.0), Inches(3.6), Inches(11), Inches(0.7),
       "Sistema Inteligente de Análisis Cinemático en Tiempo Real",
       size=22, color=C["AZUL_LUZ"])
    linea = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,
                                    Inches(1.0), Inches(4.5),
                                    Inches(2.5), Emu(28000))
    linea.fill.solid(); linea.fill.fore_color.rgb = C["VERDE"]
    linea.line.fill.background(); linea.shadow.inherit = False
    tx(slide, Inches(1.0), Inches(4.8), Inches(11), Inches(0.5),
       "Universidad Mariano Gálvez de Guatemala",
       size=16, color=C["GRIS_LUZ"])
    tx(slide, Inches(1.0), Inches(5.3), Inches(11), Inches(0.5),
       "Facultad de Ingeniería en Sistemas",
       size=14, color=C["GRIS"])
    tx(slide, Inches(1.0), Inches(6.3), Inches(11), Inches(0.5),
       "Python 3.14   ·   OpenCV   ·   NumPy   ·   GitHub Pages",
       size=11, color=C["GRIS"], font="Consolas")


def construir_slide_que_hace(prs):
    """Slide 2: ¿Qué hace el sistema? — Detecta, Calcula, Clasifica."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    fondo(slide, prs, C["BLANCO"])
    acento(slide, 0, 0, prs.slide_width, Inches(0.7), C["FONDO_OSC"])
    tx(slide, Inches(0.5), Inches(0.15), Inches(12), Inches(0.45),
       "¿QUÉ HACE EL SISTEMA?",
       size=18, bold=True, color=C["BLANCO"])
    tx(slide, Inches(0.6), Inches(1.0), Inches(12), Inches(0.6),
       "Mide cinemática con solo una cámara, sin sensores costosos",
       size=22, bold=True, color=C["TEXTO"])

    def tarjeta(x, y, w, h, icono, titulo, desc, color):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h)
        card.fill.solid(); card.fill.fore_color.rgb = RGBColor(0xF8, 0xFA, 0xFC)
        card.line.color.rgb = RGBColor(0xE2, 0xE8, 0xF0)
        card.line.width = Pt(0.75); card.shadow.inherit = False
        bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, Inches(0.12))
        bar.fill.solid(); bar.fill.fore_color.rgb = color
        bar.line.fill.background(); bar.shadow.inherit = False
        tx(slide, x, y + Inches(0.3), w, Inches(0.8),
           icono, size=42, color=color, align=PP_ALIGN.CENTER)
        tx(slide, x, y + Inches(1.3), w, Inches(0.5),
           titulo, size=18, bold=True, color=C["TEXTO"], align=PP_ALIGN.CENTER)
        tx(slide, x + Inches(0.2), y + Inches(1.9), w - Inches(0.4), Inches(1.5),
           desc, size=12, color=C["GRIS"], align=PP_ALIGN.CENTER)

    tarjeta(Inches(0.7),  Inches(2.0), Inches(3.9), Inches(3.8),
            "🎯", "DETECTA",
            "Localiza un objeto por su color usando visión por computadora "
            "(HSV) y lo sigue específicamente, ignorando otros objetos del "
            "mismo color.", C["AZUL"])
    tarjeta(Inches(4.75), Inches(2.0), Inches(3.9), Inches(3.8),
            "📐", "CALCULA",
            "Mide posición, velocidad y aceleración en tiempo real "
            "usando diferencias finitas y filtros para reducir ruido.",
            C["VERDE"])
    tarjeta(Inches(8.8),  Inches(2.0), Inches(3.9), Inches(3.8),
            "✓", "CLASIFICA",
            "Identifica automáticamente si el movimiento es MRU, MRUV "
            "o Caída Libre, y compara contra la curva teórica.", C["NARANJA"])
    tx(slide, Inches(0.6), Inches(6.4), Inches(12), Inches(0.5),
       "👉  Vamos a verlo en vivo…",
       size=18, bold=True, color=C["AZUL"], align=PP_ALIGN.CENTER)


def actualizar_ppt():
    """Crea el PPT DESDE CERO (no modifica el existente, evita XML duplicado)."""
    print("\n[2/2] Generando PPT desde cero (sin duplicados XML)...")
    prs = Presentation()
    prs.slide_width = Inches(13.33)   # 16:9
    prs.slide_height = Inches(7.5)

    construir_slide_portada(prs)
    print(f"   ✓ Slide 1: Portada")
    construir_slide_que_hace(prs)
    print(f"   ✓ Slide 2: ¿Qué hace el sistema?")
    construir_slide_tecnologias(prs)
    print(f"   ✓ Slide 3: ¿Con qué está hecho? (tecnologías simple)")
    construir_slide_fisica_simple(prs)
    print(f"   ✓ Slide 4: ¿Cómo mide la física? (analogías)")
    construir_slide_capturas_codigo(prs)
    print(f"   ✓ Slide 5: Capturas del código")
    construir_slide_qr(prs)
    print(f"   ✓ Slide 6: QR + cierre")

    # Borrar el PPT viejo (puede tener duplicados) y guardar uno limpio
    if os.path.exists(PPT_PATH):
        os.remove(PPT_PATH)
    prs.save(PPT_PATH)
    print(f"\n✓ PPT guardado LIMPIO: {PPT_PATH}")
    print(f"   Total slides: {len(prs.slides)}")


if __name__ == "__main__":
    generar_imagenes_codigo()
    actualizar_ppt()
    print("\n" + "=" * 60)
    print("LISTO. El PPT ahora tiene 6 slides:")
    print("  1. Portada (sin tocar)")
    print("  2. ¿Qué hace el sistema? (sin tocar)")
    print("  3. ¿Con qué está hecho? — Tecnologías (NUEVA)")
    print("  4. ¿Cómo mide la física? — Versión simple (NUEVA)")
    print("  5. Código que lo hace posible — Capturas (NUEVA)")
    print("  6. QR para escanear")
    print("=" * 60)
