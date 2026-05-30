"""
Genera un documento Word con el guion de la exposicion de Jose Angel
(la parte de explicar las 3 capturas de codigo).
"""
import os
import sys
from docx import Document
from docx.shared import Pt, RGBColor, Cm, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

OUT = (r"C:\Users\josea\OneDrive\Documentos\U\Fisica I\Proyecto Final"
       r"\Guion_Exposicion_JoseAngel.docx")

doc = Document()

# Margenes
section = doc.sections[0]
section.top_margin = Cm(2)
section.bottom_margin = Cm(2)
section.left_margin = Cm(2.2)
section.right_margin = Cm(2.2)

# Colores
AZUL_OSC  = RGBColor(0x0F, 0x17, 0x2A)
AZUL      = RGBColor(0x25, 0x63, 0xEB)
VERDE     = RGBColor(0x10, 0xB9, 0x81)
NARANJA   = RGBColor(0xF5, 0x9E, 0x0B)
PURPURA   = RGBColor(0x8B, 0x5C, 0xF6)
ROJO      = RGBColor(0xEF, 0x44, 0x44)
GRIS      = RGBColor(0x64, 0x74, 0x8B)
GRIS_OSC  = RGBColor(0x33, 0x41, 0x55)


def parrafo(texto, size=11, bold=False, italic=False, color=None,
            align=WD_ALIGN_PARAGRAPH.LEFT, space_after=4, font="Calibri"):
    p = doc.add_paragraph()
    p.alignment = align
    p.paragraph_format.space_after = Pt(space_after)
    run = p.add_run(texto)
    run.font.name = font
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    if color is not None:
        run.font.color.rgb = color
    return p


def heading(texto, size=14, color=AZUL_OSC, bg_color=None):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(6)
    run = p.add_run(texto)
    run.font.name = "Calibri"
    run.font.size = Pt(size)
    run.bold = True
    run.font.color.rgb = color
    # Background color (shading) si se especifica
    if bg_color is not None:
        pPr = p._p.get_or_add_pPr()
        shd = OxmlElement("w:shd")
        shd.set(qn("w:val"), "clear")
        shd.set(qn("w:color"), "auto")
        shd.set(qn("w:fill"), bg_color)
        pPr.append(shd)
    return p


def code_block(text):
    """Bloque de codigo con fondo gris."""
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(6)
    pPr = p._p.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), "F1F5F9")  # gris claro
    pPr.append(shd)
    run = p.add_run(text)
    run.font.name = "Consolas"
    run.font.size = Pt(9.5)
    run.font.color.rgb = GRIS_OSC


def linea_horizontal():
    p = doc.add_paragraph()
    pPr = p._p.get_or_add_pPr()
    pbdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), "6")
    bottom.set(qn("w:space"), "1")
    bottom.set(qn("w:color"), "CBD5E1")
    pbdr.append(bottom)
    pPr.append(pbdr)


def script_box(texto_accion, texto_decir, color_borde=AZUL):
    """Caja con accion (cursiva) + lo que se dice (negrita)."""
    # Linea de accion
    p1 = doc.add_paragraph()
    p1.paragraph_format.space_after = Pt(2)
    r1 = p1.add_run(f"▸ {texto_accion}")
    r1.font.name = "Calibri"
    r1.font.size = Pt(9)
    r1.italic = True
    r1.font.color.rgb = GRIS

    # Linea de lo que se dice
    p2 = doc.add_paragraph()
    p2.paragraph_format.space_after = Pt(10)
    p2.paragraph_format.left_indent = Cm(0.5)
    r2 = p2.add_run(f"« {texto_decir} »")
    r2.font.name = "Calibri"
    r2.font.size = Pt(11)
    r2.font.color.rgb = AZUL_OSC


# ═══════════════════════════════════════════════════════════
# PORTADA
# ═══════════════════════════════════════════════════════════
parrafo("GUION DE EXPOSICIÓN", size=10, bold=True, color=GRIS,
        align=WD_ALIGN_PARAGRAPH.CENTER)
parrafo("Explicación del Código", size=22, bold=True, color=AZUL_OSC,
        align=WD_ALIGN_PARAGRAPH.CENTER, space_after=6)
parrafo("Proyecto Final · Física I  ·  PhysicsMotionAnalyzer",
        size=11, italic=True, color=GRIS,
        align=WD_ALIGN_PARAGRAPH.CENTER, space_after=2)
parrafo("Jose Angel Gonzalez Gordillo  ·  Universidad Mariano Gálvez",
        size=10, italic=True, color=GRIS,
        align=WD_ALIGN_PARAGRAPH.CENTER, space_after=18)

linea_horizontal()

# Resumen / instrucciones
heading("📋  Cómo usar este guion", size=12)
parrafo("Este documento contiene TU parte de la exposición: explicar las "
        "3 capturas de código de la diapositiva 5.")
parrafo("• Las líneas en gris cursiva (▸) indican QUÉ señalar con el "
        "cursor o puntero.", size=10)
parrafo("• Las líneas entre comillas (« ») son lo que TENÉS que decir.", size=10)
parrafo("• Cada captura dura ~1 minuto. Total: 3 minutos.", size=10, space_after=14)


# ═══════════════════════════════════════════════════════════
# CAPTURA 1
# ═══════════════════════════════════════════════════════════
heading("📸 CAPTURA 1  —  🟠 Detección por color HSV  (~1 min)",
        size=13, color=NARANJA, bg_color="FFF7ED")

parrafo("Código en la pantalla:", size=9, bold=True, color=GRIS)
code_block("""def generar_mascara(frame_bgr, hsv_min, hsv_max, blur_ksize=9):
    \"\"\"Genera máscara binaria del objeto por color HSV.\"\"\"
    # 1) Suavizar la imagen
    desenfocado = cv2.GaussianBlur(frame_bgr, (blur_ksize, blur_ksize), 0)
    # 2) Convertir de BGR a HSV
    hsv = cv2.cvtColor(desenfocado, cv2.COLOR_BGR2HSV)
    # 3) Crear máscara
    lower = np.array(hsv_min, dtype=np.uint8)
    upper = np.array(hsv_max, dtype=np.uint8)
    mask  = cv2.inRange(hsv, lower, upper)
    # 4) Limpiar ruido
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)
    return mask""")

parrafo("Lo que decís:", size=10, bold=True, color=NARANJA, space_after=4)

script_box("Señalás 'def generar_mascara'",
    "Esta es la función principal de detección. Le entregamos un cuadro del video "
    "y dos valores: el color mínimo y el color máximo que estamos buscando — por "
    "ejemplo, el rango del color naranja.")

script_box("Señalás 'cv2.GaussianBlur'",
    "Primero, el sistema suaviza la imagen. Esto es como aplicar un desenfoque ligero "
    "para que los pixeles rugosos o con ruido no confundan la detección.")

script_box("Señalás 'cv2.cvtColor'",
    "Después convierte la imagen al formato HSV. HSV separa el color del brillo, "
    "por eso lo usamos en lugar del formato común RGB: así, si hay sombras o cambia "
    "un poco la luz, el sistema sigue reconociendo el color de la pelota.")

script_box("Señalás 'cv2.inRange'",
    "Acá pasa la magia: el sistema recorre cada pixel de la imagen y se pregunta: "
    "¿este color está dentro del rango naranja que estoy buscando? Si la respuesta "
    "es sí, lo pinta de blanco. Si la respuesta es no, lo pinta de negro. El resultado "
    "es como una silueta de la pelota.")

script_box("Señalás 'cv2.erode' y 'cv2.dilate'",
    "Finalmente, hace una limpieza. Erode elimina los puntitos blancos sueltos que "
    "pudieran ser ruido. Dilate rellena pequeños huecos dentro de la silueta. Así "
    "nos queda una silueta limpia de la pelota.")

script_box("Señalás 'return mask'",
    "Y devuelve esa silueta para que el resto del programa la use.")


# ═══════════════════════════════════════════════════════════
# CAPTURA 2
# ═══════════════════════════════════════════════════════════
heading("📸 CAPTURA 2  —  📐 Cálculos de Física  (~1 min)",
        size=13, color=VERDE, bg_color="F0FDF4")

parrafo("Código en la pantalla:", size=9, bold=True, color=GRIS)
code_block("""def derivada_central(x, t):
    \"\"\"Velocidad: cuánto cambió la posición entre dos cuadros.\"\"\"
    x = np.asarray(x); t = np.asarray(t)
    v = np.zeros_like(x)
    # Diferencias finitas centrales
    for i in range(1, len(x) - 1):
        v[i] = (x[i+1] - x[i-1]) / (t[i+1] - t[i-1])
    return v


def segunda_derivada(x, t):
    \"\"\"Aceleración: cuánto cambió la velocidad.\"\"\"
    v = derivada_central(x, t)
    a = derivada_central(v, t)
    return a""")

parrafo("Lo que decís:", size=10, bold=True, color=VERDE, space_after=4)

script_box("Señalás la función 'derivada_central'",
    "Una vez que el sistema ya rastreó la pelota durante todo el video, tenemos "
    "una lista con todas las posiciones que tuvo y los tiempos en que pasó por "
    "cada una. Esta función calcula la velocidad a partir de esa lista.")

script_box("Señalás 'v = np.zeros_like(x)'",
    "Acá creamos una lista vacía del mismo tamaño que las posiciones — será donde "
    "vamos a guardar las velocidades calculadas.")

script_box("Señalás el 'for i in range(...)'",
    "Después recorremos cada momento del video y aplicamos una fórmula matemática "
    "para calcular qué tan rápido se estaba moviendo en ese instante.")

script_box("Señalás la fórmula  v[i] = (x[i+1] − x[i-1]) / (t[i+1] − t[i-1])",
    "La fórmula es simple: tomamos la posición de un momento después y le restamos "
    "la posición de un momento antes, eso nos dice cuánto se desplazó. Y lo dividimos "
    "entre el tiempo que pasó. Eso es velocidad: distancia dividida tiempo. "
    "Usamos el cuadro anterior y el siguiente, no el actual, porque es más preciso "
    "— es una técnica que se llama 'diferencias centrales' y reduce el error.")

script_box("Pasás a la función 'segunda_derivada'",
    "Ahora, ¿cómo calculamos la aceleración? Muy fácil: es exactamente lo mismo "
    "pero aplicado a la velocidad.")

script_box("Señalás las dos líneas dentro de segunda_derivada",
    "Mira: primero calculamos la velocidad, y después aplicamos la misma cuenta "
    "pero ahora sobre las velocidades. Eso nos dice cuánto está cambiando la "
    "velocidad — o sea, cuánto está acelerando.")

parrafo("💡 ANALOGÍA por si querés agregarla:", size=9, bold=True,
        color=VERDE, space_after=2)
parrafo("« Es como si un policía midiera la velocidad de un auto: ve dónde "
        "estaba hace un segundo, dónde está ahora, resta y divide. Acá "
        "hacemos lo mismo, pero cuadro por cuadro con la pelota. »",
        size=10, italic=True, color=GRIS_OSC, space_after=12)


# ═══════════════════════════════════════════════════════════
# CAPTURA 3
# ═══════════════════════════════════════════════════════════
heading("📸 CAPTURA 3  —  🎯 Clasificación del Movimiento  (~1 min)",
        size=13, color=PURPURA, bg_color="FAF5FF")

parrafo("Código en la pantalla:", size=9, bold=True, color=GRIS)
code_block("""def clasificar_movimiento(a_array, v_array=None,
                           umbral_mru=0.5, umbral_g=1.5):
    \"\"\"Decide si es MRU, MRUV o Caída Libre según la aceleración.\"\"\"
    a_prom = float(np.nanmean(a_array))
    v_prom = float(np.nanmean(v_array)) if v_array is not None else 0

    # Si la aceleración es casi cero → velocidad constante
    if abs(a_prom) < umbral_mru:
        return "MRU", a_prom, v_prom

    # Si la aceleración es cercana a la gravedad → caída libre
    if abs(abs(a_prom) - 9.8) < umbral_g:
        return "Caída Libre", a_prom, v_prom

    # Cualquier otra aceleración constante → MRUV
    return "MRUV", a_prom, v_prom""")

parrafo("Lo que decís:", size=10, bold=True, color=PURPURA, space_after=4)

script_box("Señalás 'def clasificar_movimiento'",
    "Esta función es la que decide qué tipo de movimiento estamos observando "
    "— y lo hace automáticamente, sin que el usuario tenga que indicarlo.")

script_box("Señalás 'a_prom = float(np.nanmean(a_array))'",
    "Primero, el sistema calcula el promedio de todas las aceleraciones que "
    "midió durante el video. Ese promedio es la clave para decidir.")

script_box("Señalás el primer 'if abs(a_prom) < umbral_mru'",
    "Después se hace 3 preguntas en orden. Primera pregunta: ¿La aceleración "
    "promedio es casi cero? Si la respuesta es sí, significa que la pelota se "
    "movía a velocidad constante — y eso es un MRU, Movimiento Rectilíneo "
    "Uniforme. El sistema responde 'MRU'.")

script_box("Señalás el segundo 'if abs(abs(a_prom) - 9.8) < umbral_g'",
    "Segunda pregunta: si no es MRU, entonces ¿la aceleración es cercana a 9.8? "
    "Porque 9.8 es la aceleración de la gravedad de la Tierra. Si la respuesta "
    "es sí, significa que solo la gravedad está actuando — y eso es Caída Libre.")

script_box("Señalás 'return MRUV'",
    "Tercera opción: si no es ni MRU ni Caída Libre, pero sí hay aceleración, "
    "entonces es un MRUV — Movimiento Rectilíneo Uniformemente Variado. Es decir, "
    "hay una aceleración constante pero no es la gravedad.")

script_box("Cierre",
    "Lo bonito de esto es que el sistema deduce solo qué tipo de física está "
    "pasando, basándose en los datos que midió. Le dimos al programa la "
    "inteligencia para reconocer los movimientos por sí mismo.")


# ═══════════════════════════════════════════════════════════
# RESUMEN FINAL
# ═══════════════════════════════════════════════════════════
linea_horizontal()
heading("🎤 RESUMEN FINAL  (15 segundos)", size=13, color=AZUL)

parrafo("Antes de pasar a la siguiente diapositiva, decís esto:", size=10,
        italic=True, color=GRIS)

p = doc.add_paragraph()
pPr = p._p.get_or_add_pPr()
shd = OxmlElement("w:shd")
shd.set(qn("w:val"), "clear")
shd.set(qn("w:color"), "auto")
shd.set(qn("w:fill"), "DBEAFE")
pPr.append(shd)
p.paragraph_format.space_after = Pt(10)
run = p.add_run(
    "« Entonces, en resumen: primero el código encuentra la pelota usando "
    "detección por color. Después calcula su velocidad y aceleración con "
    "fórmulas matemáticas simples. Y finalmente decide automáticamente qué "
    "tipo de movimiento es. Todo esto en tiempo real, cuadro por cuadro. »"
)
run.font.name = "Calibri"
run.font.size = Pt(11)
run.bold = True
run.font.color.rgb = AZUL_OSC


# ═══════════════════════════════════════════════════════════
# VERSION CORTA DE EMERGENCIA
# ═══════════════════════════════════════════════════════════
linea_horizontal()
heading("⚡ VERSIÓN CORTA  (si te trabás o te ponés nervioso)", size=13,
        color=ROJO)

parrafo("Si te quedás en blanco, decí solo esto y ya cumpliste tu parte:",
        size=10, italic=True, color=GRIS, space_after=6)

bullets = [
    ("[Señalás imagen 1]", "La primera parte encuentra la pelota en el video "
                            "usando detección por color HSV."),
    ("[Señalás imagen 2]", "La segunda mide la velocidad y aceleración "
                            "comparando cómo cambia la posición entre cuadros."),
    ("[Señalás imagen 3]", "La tercera decide automáticamente si el movimiento "
                            "es MRU, MRUV o Caída Libre según la aceleración medida."),
    ("[Cierre]", "Todo esto sucede en tiempo real."),
]
for accion, texto in bullets:
    p1 = doc.add_paragraph()
    p1.paragraph_format.space_after = Pt(2)
    r1 = p1.add_run(f"▸ {accion}")
    r1.italic = True; r1.font.size = Pt(9); r1.font.color.rgb = GRIS
    p2 = doc.add_paragraph()
    p2.paragraph_format.left_indent = Cm(0.5)
    p2.paragraph_format.space_after = Pt(8)
    r2 = p2.add_run(f"« {texto} »")
    r2.font.size = Pt(11); r2.font.color.rgb = AZUL_OSC


# ═══════════════════════════════════════════════════════════
# TIPS Y REGLAS
# ═══════════════════════════════════════════════════════════
linea_horizontal()
heading("💡 REGLAS DE ORO", size=13, color=AZUL_OSC)

parrafo("Para que se entienda mejor:", size=10, italic=True, color=GRIS,
        space_after=6)

reglas = [
    ("array", "lista de valores"),
    ("función", "esta parte del código / este bloque"),
    ("if", "se pregunta si..."),
    ("return", "devuelve / entrega"),
    ("loop / for", "recorre cada uno / va uno por uno"),
    ("variable", "valor que guardamos"),
    ("umbral", "valor límite"),
]
parrafo("En vez de decir...                  Mejor decí...",
        size=10, bold=True, color=GRIS_OSC, font="Consolas", space_after=4)
for tec, normal in reglas:
    parrafo(f"  {tec:<30s} {normal}", size=10, color=GRIS_OSC,
            font="Consolas", space_after=2)

doc.add_paragraph()
heading("⚠️ FRASES SALVAVIDAS  (por si te trabás)", size=12, color=ROJO)

salvavidas = [
    "Si te quedás en blanco:",
    "« Básicamente, lo que hace este código es… encontrar la pelota / medir "
    "su movimiento / decidir el tipo. »",
    "",
    "Si te preguntan algo difícil:",
    "« Buena pregunta. Para ser preciso, ese detalle lo manejamos con "
    "[OpenCV / NumPy / la fórmula que aparezca en el código]. »",
    "",
    "Si te olvidás un término técnico:",
    "« Es una técnica estándar de visión por computadora / cálculo numérico. »",
]
for s in salvavidas:
    if s == "":
        doc.add_paragraph()
        continue
    if s.startswith("«"):
        parrafo(s, size=11, italic=True, color=AZUL_OSC, space_after=4)
    else:
        parrafo(s, size=10, bold=True, color=GRIS_OSC, space_after=2)


# Guardar
doc.save(OUT)
print(f"Guion guardado: {OUT}")
print(f"Tamaño: {os.path.getsize(OUT)/1024:.1f} KB")
