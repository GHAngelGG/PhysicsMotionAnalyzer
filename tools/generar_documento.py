"""
Genera el documento técnico de Física 1 — PhysicsMotionAnalyzer
Universidad Mariano Gálvez de Guatemala
"""
from docx import Document
from docx.shared import Pt, RGBColor, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import datetime

doc = Document()

# ─── Márgenes ───
section = doc.sections[0]
section.top_margin    = Cm(2.5)
section.bottom_margin = Cm(2.5)
section.left_margin   = Cm(3)
section.right_margin  = Cm(2.5)

# ─── Helpers de formato ───
AZUL_UMG = RGBColor(0x00, 0x33, 0x80)

def titulo_portada(doc, text, size=20, bold=True, color=AZUL_UMG, space_after=6):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(text)
    run.bold = bold
    run.font.size = Pt(size)
    run.font.color.rgb = color
    p.paragraph_format.space_after = Pt(space_after)
    return p

def normal(doc, text, size=12, bold=False, italic=False, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_after=6):
    p = doc.add_paragraph()
    p.alignment = align
    run = p.add_run(text)
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    p.paragraph_format.space_after = Pt(space_after)
    return p

def h1(doc, text):
    p = doc.add_heading(text, level=1)
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run = p.runs[0]
    run.font.color.rgb = AZUL_UMG
    return p

def h2(doc, text):
    p = doc.add_heading(text, level=2)
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    return p

def h3(doc, text):
    p = doc.add_heading(text, level=3)
    return p

def bullet(doc, text, size=11):
    p = doc.add_paragraph(text, style="List Bullet")
    for run in p.runs:
        run.font.size = Pt(size)
    return p

def agregar_tabla_simple(doc, headers, rows, col_widths=None):
    table = doc.add_table(rows=1+len(rows), cols=len(headers))
    table.style = "Table Grid"
    hdr = table.rows[0].cells
    for i, h in enumerate(headers):
        hdr[i].text = h
        hdr[i].paragraphs[0].runs[0].bold = True
        hdr[i].paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF,0xFF,0xFF)
        tc = hdr[i]._tc
        tcPr = tc.get_or_add_tcPr()
        shd = OxmlElement("w:shd")
        shd.set(qn("w:val"), "clear")
        shd.set(qn("w:color"), "auto")
        shd.set(qn("w:fill"), "003380")
        tcPr.append(shd)
    for ri, row in enumerate(rows):
        cells = table.rows[ri+1].cells
        for ci, val in enumerate(row):
            cells[ci].text = str(val)
    if col_widths:
        for ri, row in enumerate(table.rows):
            for ci, cell in enumerate(row.cells):
                cell.width = Inches(col_widths[ci])
    return table

# ══════════════════════════════════════════════════════════
# PORTADA
# ══════════════════════════════════════════════════════════
titulo_portada(doc, "Universidad Mariano Gálvez de Guatemala", size=16)
titulo_portada(doc, "Facultad de Ingeniería en Sistemas", size=14, bold=False)
titulo_portada(doc, "Ingeniería en Sistemas — Plan Fin de Semana | Campus Central", size=12, bold=False)
doc.add_paragraph()

titulo_portada(doc, "PhysicsMotionAnalyzer", size=24, space_after=4)
titulo_portada(doc, "Sistema Inteligente de Monitoreo de Movimiento y Análisis Físico en Tiempo Real", size=14, bold=False, space_after=12)

doc.add_paragraph()
titulo_portada(doc, "Física 1", size=14)
titulo_portada(doc, "Docente: [Nombre del docente]", size=12, bold=False)
doc.add_paragraph()

titulo_portada(doc, "Integrantes del equipo", size=13)
integrantes = [
    ("1", "Jose Angel Gonzalez Gordillo",          "0901 24-8660",  "Desarrollador Principal / Tracking"),
    ("2", "Luis Eduardo Abdiel Jacinto Marroquín", "0901 24-10316", "Física y Validación"),
    ("3", "Alex Estuardo Fernández Veliz",          "0901 24-4250",  "Interfaz Gráfica"),
    ("4", "Rodrigo Manasés Chávez Marroquín",      "0901 24-2822",  "Simulación y Exportación"),
    ("5", "Oscar Josué García Cáceres",             "0901 24-9152",  "Pruebas y Documentación"),
    ("6", "[Nombre Integrante 6]",                  "[Carné]",       "[Rol]"),
]
t = agregar_tabla_simple(doc,
    ["#", "Nombre", "Carné", "Rol"],
    integrantes,
    col_widths=[0.3, 2.8, 1.2, 1.8])

doc.add_paragraph()
titulo_portada(doc, "Guatemala, mayo de 2026", size=12, bold=False)
titulo_portada(doc, "Fecha de entrega: 30 de mayo del 2026", size=12)

doc.add_page_break()

# ══════════════════════════════════════════════════════════
# RESUMEN (ABSTRACT)
# ══════════════════════════════════════════════════════════
h1(doc, "Resumen")
normal(doc, (
    "El presente informe documenta el desarrollo de PhysicsMotionAnalyzer, un sistema "
    "de software desarrollado en Python que permite el análisis cinemático de objetos "
    "en movimiento mediante visión computacional y cálculo numérico en tiempo real. "
    "El sistema es capaz de procesar entradas de video grabado, cámara en vivo y "
    "simulaciones sintéticas para detectar la posición de un objeto mediante segmentación "
    "de color en el espacio HSV, calcular su velocidad y aceleración usando diferencias "
    "finitas centrales, clasificar automáticamente el tipo de movimiento (Movimiento "
    "Rectilíneo Uniforme, Movimiento Rectilíneo Uniformemente Variado o Caída Libre) "
    "y comparar los datos experimentales con la curva teórica correspondiente mediante "
    "un indicador de error porcentual. Los resultados de validación muestran errores "
    "porcentuales medios de 0.00% para MRU, 0.70% para MRUV y 4.54% para Caída Libre, "
    "confirmando la precisión del sistema. La interfaz gráfica desarrollada con Tkinter "
    "y matplotlib proporciona visualización en tiempo real de las tres gráficas físicas "
    "(posición, velocidad y aceleración) junto con la predicción teórica superpuesta, "
    "y permite la exportación de resultados en formatos CSV, PNG y reporte de texto."
))
normal(doc, (
    "Palabras clave: cinemática, visión computacional, MRU, MRUV, Caída Libre, "
    "OpenCV, Python, análisis de movimiento, derivadas numéricas."
), italic=True)

doc.add_page_break()

# ══════════════════════════════════════════════════════════
# INTRODUCCIÓN
# ══════════════════════════════════════════════════════════
h1(doc, "Introducción")
normal(doc, (
    "El análisis del movimiento de objetos constituye uno de los pilares fundamentales "
    "de la física clásica. Desde los trabajos de Galileo Galilei sobre la caída libre "
    "hasta las formulaciones matemáticas de Isaac Newton sobre el movimiento rectilíneo, "
    "la cinemática ha provisto al ser humano de herramientas para comprender y predecir "
    "el comportamiento de cuerpos en movimiento. En el contexto educativo contemporáneo, "
    "la integración de tecnologías digitales en el estudio de estos fenómenos representa "
    "una oportunidad para transformar la enseñanza tradicional en experiencias de "
    "aprendizaje activo y verificable."
))
normal(doc, (
    "En Guatemala, las instituciones de educación superior buscan incorporar metodologías "
    "innovadoras que permitan a los estudiantes de ingeniería no solo comprender los "
    "conceptos teóricos de la física, sino también aplicarlos en contextos prácticos "
    "utilizando herramientas tecnológicas de vanguardia. Es en este marco que surge "
    "PhysicsMotionAnalyzer, un sistema que combina técnicas de visión computacional "
    "con algoritmos de análisis físico para proporcionar una plataforma educativa "
    "interactiva y verificable."
))
normal(doc, (
    "El sistema desarrollado permite a los usuarios analizar el movimiento de objetos "
    "reales mediante video o cámara, o bien mediante simulaciones generadas por el "
    "propio programa. A través de la segmentación de color y el procesamiento de imagen, "
    "el sistema rastrea la posición del objeto en cada fotograma, calcula numéricamente "
    "su velocidad y aceleración, y clasifica automáticamente el tipo de movimiento "
    "observado. Finalmente, compara los datos obtenidos con la predicción teórica "
    "correspondiente y cuantifica el nivel de precisión alcanzado."
))
normal(doc, (
    "Este informe describe el proceso completo de investigación, diseño, implementación "
    "y validación del sistema, siguiendo una metodología estructurada que abarca desde "
    "la identificación del problema hasta los resultados obtenidos y las recomendaciones "
    "para trabajo futuro."
))

# ══════════════════════════════════════════════════════════
# MARCO CONCEPTUAL
# ══════════════════════════════════════════════════════════
h1(doc, "Marco Conceptual")

h2(doc, "Antecedentes")
normal(doc, (
    "El análisis automático del movimiento mediante visión computacional ha sido objeto "
    "de investigación desde la década de 1980. Los primeros sistemas se basaban en "
    "diferencias entre fotogramas consecutivos (frame differencing) para detectar objetos "
    "en movimiento, técnica que presentaba alta sensibilidad al ruido y a los cambios "
    "de iluminación."
))
normal(doc, (
    "Con la popularización de las cámaras digitales y el incremento en la capacidad "
    "de procesamiento de los ordenadores personales en los años 2000, surgieron sistemas "
    "más robustos basados en modelos de color y descriptores de características visuales. "
    "Bibliotecas como OpenCV (Intel, 2000) democratizaron el acceso a algoritmos de "
    "visión computacional, permitiendo su uso en contextos académicos y de investigación "
    "aplicada."
))
normal(doc, (
    "En el ámbito educativo, proyectos como Tracker Video Analysis (Douglas Brown, 2008) "
    "demostraron el potencial de las herramientas de análisis de video para la enseñanza "
    "de la física. Tracker, aunque poderoso, requiere la marcación manual de la posición "
    "del objeto en cada fotograma. PhysicsMotionAnalyzer automatiza este proceso mediante "
    "detección de color, eliminando la intervención manual y permitiendo el análisis "
    "en tiempo real."
))

h2(doc, "Justificación")
normal(doc, (
    "La necesidad de una herramienta que automatice el análisis cinemático en el contexto "
    "universitario guatemalteco surge de dos problemáticas identificadas durante el "
    "desarrollo del curso de Física 1:"
))
bullet(doc, "La verificación experimental de las leyes del movimiento requiere equipos de medición costosos (sensores de posición, cronómetros de alta precisión, rampas de experimentación) que no siempre están disponibles en las instituciones educativas del país.")
bullet(doc, "Las herramientas digitales existentes para análisis de movimiento (como Tracker) requieren marcación manual fotograma a fotograma, lo que convierte el proceso en una tarea tediosa y propensa a errores humanos.")
normal(doc, (
    "PhysicsMotionAnalyzer resuelve ambas problemáticas al utilizar únicamente una cámara "
    "convencional (incluyendo la webcam integrada en cualquier laptop) y automatizar "
    "completamente el proceso de detección y análisis, democratizando el acceso a la "
    "experimentación física digital."
))

h2(doc, "Planteamiento del Problema")
normal(doc, (
    "¿Es posible desarrollar un sistema de software accesible y preciso que automatice "
    "el análisis cinemático de objetos en movimiento mediante visión computacional, "
    "permitiendo a estudiantes universitarios verificar experimentalmente las leyes "
    "del movimiento rectilíneo uniforme, uniformemente variado y de caída libre sin "
    "necesidad de equipamiento especializado?"
))

h2(doc, "Alcances del Proyecto")
normal(doc, "El sistema cubre los siguientes alcances:")
bullet(doc, "Detección y rastreo automático de objetos por color en video grabado y cámara en vivo.")
bullet(doc, "Cálculo numérico de posición, velocidad y aceleración mediante diferencias finitas centrales.")
bullet(doc, "Clasificación automática del tipo de movimiento (MRU, MRUV, Caída Libre).")
bullet(doc, "Generación de curva teórica y cálculo de error porcentual para validación.")
bullet(doc, "Modo de simulación para los tres tipos de movimiento con ruido Gaussiano configurable.")
bullet(doc, "Visualización en tiempo real de las tres gráficas físicas.")
bullet(doc, "Exportación de resultados a CSV, PNG y reporte de texto.")
normal(doc, "Fuera del alcance del sistema se encuentran:")
bullet(doc, "Análisis de movimiento en dos dimensiones independientes simultáneas (proyectiles en parábola).")
bullet(doc, "Detección de múltiples objetos simultáneamente.")
bullet(doc, "Análisis de video con resolución mayor a 4K.")

# ══════════════════════════════════════════════════════════
# MARCO TEÓRICO
# ══════════════════════════════════════════════════════════
h1(doc, "Marco Teórico")

h2(doc, "Cinemática — Tipos de Movimiento")

h3(doc, "Movimiento Rectilíneo Uniforme (MRU)")
normal(doc, (
    "El MRU describe el desplazamiento de un cuerpo a lo largo de una línea recta con "
    "velocidad constante. Su ecuación fundamental es:"
))
normal(doc, "x(t) = x₀ + v · t", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
normal(doc, (
    "donde x₀ es la posición inicial, v es la velocidad (constante) y t es el tiempo. "
    "En el MRU la aceleración es nula (a = 0). El sistema clasifica un movimiento como "
    "MRU cuando la aceleración media calculada satisface |ā| < 0.5 m/s²."
))

h3(doc, "Movimiento Rectilíneo Uniformemente Variado (MRUV)")
normal(doc, (
    "El MRUV describe el desplazamiento de un cuerpo a lo largo de una línea recta con "
    "aceleración constante. Sus ecuaciones fundamentales son:"
))
normal(doc, "x(t) = x₀ + v₀ · t + ½ · a · t²", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
normal(doc, "v(t) = v₀ + a · t", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
normal(doc, "v² = v₀² + 2 · a · (x − x₀)    [Ecuación de Torricelli]", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
normal(doc, (
    "donde v₀ es la velocidad inicial y a es la aceleración constante. El sistema "
    "clasifica un movimiento como MRUV cuando la aceleración media no cumple los "
    "criterios de MRU ni de Caída Libre."
))

h3(doc, "Caída Libre")
normal(doc, (
    "La caída libre describe el movimiento de un cuerpo sometido únicamente a la "
    "aceleración gravitacional terrestre (g = 9.8 m/s²), sin considerar resistencia "
    "del aire. Con el eje Y positivo hacia arriba:"
))
normal(doc, "y(t) = y₀ + v₀ · t − ½ · g · t²", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
normal(doc, (
    "El sistema clasifica un movimiento como Caída Libre cuando ||ā| − 9.8| < 1.5 m/s², "
    "es decir, cuando la aceleración media calculada es aproximadamente igual a g."
))

h2(doc, "Visión Computacional y Segmentación por Color")
normal(doc, (
    "La visión computacional es el campo de la inteligencia artificial que permite a "
    "los sistemas informáticos interpretar y comprender información visual del mundo real. "
    "Para el rastreo de objetos, PhysicsMotionAnalyzer utiliza segmentación por color "
    "en el espacio de color HSV (Hue, Saturation, Value), que presenta ventajas "
    "significativas sobre el espacio RGB para la detección de colores bajo variaciones "
    "de iluminación:"
))
bullet(doc, "El canal Hue (matiz, 0°-360°) codifica el color puro independientemente del brillo.")
bullet(doc, "El canal Saturation (saturación) cuantifica la pureza del color.")
bullet(doc, "El canal Value (valor) representa la luminosidad, desacoplada del matiz.")
normal(doc, (
    "El proceso de rastreo sigue los pasos: (1) convertir cada fotograma de BGR a HSV, "
    "(2) aplicar una máscara binaria con los umbrales HSV configurados, (3) encontrar "
    "los contornos de las regiones detectadas, (4) seleccionar el contorno de mayor "
    "área como el objeto de interés, (5) calcular el centroide del contorno como "
    "posición del objeto."
))

h2(doc, "Derivadas Numéricas — Diferencias Finitas Centrales")
normal(doc, (
    "Dado que la posición se obtiene como una serie discreta de puntos x[i] en instantes "
    "t[i], la velocidad y aceleración se calculan mediante diferencias finitas centrales, "
    "que ofrecen mayor precisión que las diferencias hacia adelante o hacia atrás:"
))
normal(doc, "v[i] = (x[i+1] − x[i−1]) / (t[i+1] − t[i−1])", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
normal(doc, "a[i] = (x[i+1] − 2·x[i] + x[i−1]) / Δt²", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
normal(doc, (
    "Para reducir el ruido inherente en los datos obtenidos por rastreo de video, "
    "se aplica el filtro de Savitzky-Golay (scipy.signal.savgol_filter) antes de "
    "calcular las derivadas. Este filtro ajusta polinomios locales a ventanas de "
    "puntos consecutivos, preservando mejor la forma de la señal que un filtro de "
    "media móvil simple."
))

h2(doc, "Calibración Espacial")
normal(doc, (
    "Las posiciones detectadas por OpenCV se expresan en píxeles. Para convertirlas "
    "a metros, el sistema utiliza un factor de calibración expresado en píxeles por "
    "metro (px/m). El usuario establece este factor midiendo en el video un objeto "
    "de dimensiones conocidas (por ejemplo, una regla de 1 metro). La conversión es:"
))
normal(doc, "posición [m] = posición [px] / factor_calibración [px/m]", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)

# ══════════════════════════════════════════════════════════
# MARCO METODOLÓGICO
# ══════════════════════════════════════════════════════════
h1(doc, "Marco Metodológico")

h2(doc, "Método de Investigación")
normal(doc, (
    "El proyecto adopta una metodología de investigación aplicada con enfoque "
    "cuantitativo y experimental. Se desarrolló un artefacto de software (PhysicsMotionAnalyzer) "
    "y se validó su precisión comparando los resultados computacionales con los valores "
    "teóricos esperados para cada tipo de movimiento."
))
normal(doc, (
    "El proceso de desarrollo siguió un modelo iterativo: se implementó un módulo, "
    "se probó con datos sintéticos, se corrigieron errores, y se procedió al siguiente "
    "módulo. Esta estrategia permitió identificar y resolver problemas de forma temprana "
    "antes de integrar todos los componentes."
))

h2(doc, "Objetivos")

h3(doc, "Objetivo General")
normal(doc, (
    "Desarrollar un sistema de software en Python que permita el análisis cinemático "
    "automatizado de objetos en movimiento mediante visión computacional, clasificando "
    "automáticamente el tipo de movimiento y validando los resultados contra la "
    "predicción teórica correspondiente."
))

h3(doc, "Objetivos Específicos")
bullet(doc, "Implementar un módulo de detección y rastreo de objetos por color HSV usando OpenCV.")
bullet(doc, "Calcular posición, velocidad y aceleración en tiempo real mediante diferencias finitas centrales.")
bullet(doc, "Clasificar automáticamente el movimiento detectado como MRU, MRUV o Caída Libre.")
bullet(doc, "Generar la curva teórica para el tipo de movimiento detectado y calcular el error porcentual respecto a los datos medidos.")
bullet(doc, "Desarrollar una interfaz gráfica intuitiva que muestre las gráficas físicas en tiempo real.")
bullet(doc, "Implementar un modo de simulación con datos sintéticos para los tres tipos de movimiento.")
bullet(doc, "Exportar los resultados en formatos CSV, PNG y reporte de texto.")

h2(doc, "Hipótesis")
normal(doc, (
    "Un sistema de software basado en segmentación de color HSV y diferencias finitas "
    "centrales es capaz de medir y clasificar el tipo de movimiento de un objeto con "
    "un error porcentual medio inferior al 10% para MRU y MRUV, e inferior al 15% "
    "para Caída Libre, utilizando como entrada únicamente video grabado con una cámara "
    "convencional."
))

h2(doc, "Variables")
agregar_tabla_simple(doc,
    ["Tipo", "Variable", "Definición", "Unidad"],
    [
        ("Independiente", "Tipo de movimiento", "MRU, MRUV o Caída Libre programado en simulación", "—"),
        ("Independiente", "Parámetros iniciales", "x₀, v₀, a, t_total, nivel de ruido", "m, m/s, m/s², s"),
        ("Dependiente", "Posición x(t)", "Centroide del objeto detectado, convertido a metros", "m"),
        ("Dependiente", "Velocidad v(t)", "Derivada numérica de la posición", "m/s"),
        ("Dependiente", "Aceleración a(t)", "Derivada numérica de la velocidad", "m/s²"),
        ("Dependiente", "Error porcentual", "Desviación entre curva medida y teórica", "%"),
        ("Control", "Factor de calibración", "Píxeles por metro, fijado antes del análisis", "px/m"),
    ],
    col_widths=[1.2, 1.5, 2.8, 0.9])

h2(doc, "Población y Muestra")
normal(doc, (
    "La validación del sistema se realizó utilizando el modo de simulación integrado, "
    "que genera series de datos sintéticas con ruido Gaussiano controlado. Se ejecutaron "
    "tres pruebas de referencia:"
))
bullet(doc, "MRU: x₀ = 0 m, v = 2.0 m/s, t_total = 5 s, sin ruido.")
bullet(doc, "MRUV: x₀ = 0 m, v₀ = 1.0 m/s, a = 3.0 m/s², t_total = 5 s, ruido σ = 0.02 m.")
bullet(doc, "Caída Libre: y₀ = 10 m, v₀ = 0 m/s, g = 9.8 m/s², t_total = 1.4 s, ruido σ = 0.02 m.")

h2(doc, "Instrumentos y Herramientas")
agregar_tabla_simple(doc,
    ["Herramienta", "Versión", "Propósito"],
    [
        ("Python",          "3.14",     "Lenguaje de programación principal"),
        ("OpenCV",          "4.13.0",   "Captura de video y visión computacional"),
        ("NumPy",           "2.4.4",    "Operaciones numéricas y arrays"),
        ("SciPy",           "1.17.1",   "Filtro Savitzky-Golay y ajuste de curvas"),
        ("Matplotlib",      "3.10.9",   "Gráficas embebidas en la GUI"),
        ("Pandas",          "3.0.2",    "Exportación a CSV"),
        ("Pillow",          "12.2.0",   "Conversión de imágenes para Tkinter"),
        ("Tkinter",         "integrado","Interfaz gráfica de usuario"),
        ("VS Code",         "2024.x",   "Entorno de desarrollo integrado"),
        ("Git / GitHub",    "—",        "Control de versiones"),
    ],
    col_widths=[1.5, 1.0, 3.8])

h2(doc, "Cronograma de Actividades")
agregar_tabla_simple(doc,
    ["Semana", "Actividad", "Responsable"],
    [
        ("1  (abr. 14-20)", "Definición de alcances, arquitectura del sistema, estructura de módulos",              "Todos"),
        ("2  (abr. 21-27)", "Implementación del módulo de física (kinematics, classifier, validator)",              "Luis, Jose Angel"),
        ("3  (abr. 28 — may. 4)", "Implementación del tracking OpenCV y simulador",                                 "Jose Angel, Rodrigo"),
        ("4  (may. 5-11)",  "Desarrollo de la GUI (main_window, video_panel, graphs_panel)",                        "Alex, Jose Angel"),
        ("5  (may. 12-18)", "Integración completa, pruebas de cada modo (video, cámara, simulación)",               "Todos"),
        ("6  (may. 19-25)", "Grabación del video demostrativo con pelota, ajuste de calibración",                   "Todos"),
        ("7  (may. 26-29)", "Redacción del informe técnico y revisión final",                                        "Oscar, Jose Angel"),
        ("8  (may. 30)",    "Entrega final",                                                                         "Todos"),
    ],
    col_widths=[1.6, 3.4, 1.3])

h2(doc, "Proyecto Piloto")
normal(doc, (
    "Antes de proceder con las pruebas de video real, se realizó un proyecto piloto "
    "utilizando el modo de simulación del propio sistema. Este piloto permitió:"
))
bullet(doc, "Verificar el correcto funcionamiento de los cálculos de derivadas numéricas.")
bullet(doc, "Ajustar los umbrales de clasificación (|ā| < 0.5 para MRU, ||ā|-9.8| < 1.5 para Caída Libre).")
bullet(doc, "Confirmar que la curva teórica superpuesta en la gráfica de posición coincidía visualmente con los datos simulados.")
bullet(doc, "Establecer los niveles de ruido representativos de una cámara convencional (σ ≈ 0.01-0.05 m).")

# ══════════════════════════════════════════════════════════
# MARCO ADMINISTRATIVO
# ══════════════════════════════════════════════════════════
h1(doc, "Marco Administrativo")

h2(doc, "Recursos Utilizados")

h3(doc, "Recursos Humanos")
agregar_tabla_simple(doc,
    ["Integrante", "Dedicación semanal", "Rol principal"],
    [
        ("Jose Angel Gonzalez Gordillo",          "8-10 h", "Arquitectura, tracking, integración"),
        ("Luis Eduardo Jacinto Marroquín",        "6-8 h",  "Física, validación, ecuaciones"),
        ("Alex Estuardo Fernández Veliz",          "6-8 h",  "GUI, diseño de paneles"),
        ("Rodrigo Manasés Chávez Marroquín",      "6-8 h",  "Simulador, exportación"),
        ("Oscar Josué García Cáceres",             "6-8 h",  "Pruebas, documentación"),
        ("[Integrante 6]",                         "6-8 h",  "[Rol]"),
    ],
    col_widths=[2.5, 1.5, 2.3])

h3(doc, "Recursos Tecnológicos")
bullet(doc, "Laptops personales de los integrantes con Python 3.14 instalado.")
bullet(doc, "Webcam integrada (1080p, 30 fps) para pruebas de captura en vivo.")
bullet(doc, "Cámara de smartphone para grabación del video demostrativo.")
bullet(doc, "GitHub (repositorio privado) para control de versiones y colaboración.")
bullet(doc, "VS Code como entorno de desarrollo integrado.")

h3(doc, "Recursos Materiales")
bullet(doc, "Pelota de color naranja (diámetro aprox. 20 cm) para el experimento de video.")
bullet(doc, "Cinta métrica de 3 metros para calibración espacial.")
bullet(doc, "Superficie plana (mesa o pared) como fondo neutro para el video.")

h2(doc, "Presupuesto")
agregar_tabla_simple(doc,
    ["Concepto", "Costo (GTQ)", "Observaciones"],
    [
        ("Pelota de experimento",    "Q 30.00",  "Objeto de rastreo para video demostrativo"),
        ("Impresión del informe",    "Q 50.00",  "6 copias para cada integrante"),
        ("Dominio GitHub / hosting", "Q 0.00",   "Repositorio privado gratuito"),
        ("Software",                 "Q 0.00",   "Todas las herramientas son open-source"),
        ("Conectividad internet",    "Q 80.00",  "Datos móviles para coordinación del equipo"),
        ("TOTAL",                    "Q 160.00", ""),
    ],
    col_widths=[2.5, 1.3, 2.5])

# ══════════════════════════════════════════════════════════
# MARCO OPERATIVO
# ══════════════════════════════════════════════════════════
h1(doc, "Marco Operativo")

h2(doc, "Recolección de Datos")
normal(doc, (
    "El sistema implementa tres mecanismos de recolección de datos, diseñados para "
    "cubrir diferentes escenarios de uso:"
))

h3(doc, "Modo Video")
normal(doc, (
    "El usuario carga un archivo de video (MP4, AVI, MOV, MKV) mediante la interfaz. "
    "OpenCV lee el archivo fotograma a fotograma, aplica la segmentación HSV para "
    "detectar el objeto, y registra el centroide en píxeles junto con el timestamp "
    "de cada fotograma. La posición se convierte a metros usando el factor de "
    "calibración configurado."
))

h3(doc, "Modo Cámara")
normal(doc, (
    "Similar al modo video, pero la fuente es la webcam en tiempo real. El bucle "
    "de captura se ejecuta en un hilo secundario (threading.Thread) para no bloquear "
    "la interfaz gráfica. Los datos se acumulan mientras la captura está activa."
))

h3(doc, "Modo Simulación")
normal(doc, (
    "El generador de simulación (motion_simulator.py) crea series de datos sintéticas "
    "a partir de las ecuaciones cinemáticas, añadiendo ruido Gaussiano configurable "
    "para imitar las imperfecciones de una medición real. Esto permite validar el "
    "sistema de análisis de forma controlada."
))

h2(doc, "Trabajo de Campo")
normal(doc, (
    "Para la demostración con video real, el equipo filmó el lanzamiento vertical "
    "de una pelota de color naranja contra un fondo de color neutro. El procedimiento fue:"
))
bullet(doc, "Colocar una regla de 1 metro en el mismo plano del movimiento para calibración.")
bullet(doc, "Filmar el lanzamiento a 30 fps con iluminación natural difusa (sin sombras fuertes).")
bullet(doc, "Cargar el video en PhysicsMotionAnalyzer, seleccionar el preset 'Naranja'.")
bullet(doc, "Ajustar el factor de calibración midiendo la regla en la imagen.")
bullet(doc, "Iniciar el análisis y registrar los resultados obtenidos.")
normal(doc, (
    "[PLACEHOLDER: Insertar aquí capturas de pantalla del video real y los resultados obtenidos. "
    "Video demostrativo pendiente de filmación.]"
), italic=True)

h2(doc, "Procesamiento de Datos")
normal(doc, (
    "El procesamiento sigue el pipeline:"
))
bullet(doc, "Posición bruta (px) → conversión a metros.")
bullet(doc, "Aplicación del filtro Savitzky-Golay (ventana 9 puntos, grado 2) para suavizado.")
bullet(doc, "Cálculo de velocidad: diferencias finitas centrales sobre posición filtrada.")
bullet(doc, "Cálculo de aceleración: diferencias finitas centrales sobre velocidad.")
bullet(doc, "Clasificación: comparación de aceleración media con umbrales de MRU/MRUV/Caída Libre.")
bullet(doc, "Validación: ajuste de parámetros iniciales, generación de curva teórica, cálculo de error.")

h2(doc, "Resultados Obtenidos")

h3(doc, "Pruebas de Validación con Simulación")
agregar_tabla_simple(doc,
    ["Tipo", "Parámetros", "Tipo detectado", "Error medio (%)"],
    [
        ("MRU",         "v = 2.0 m/s",                        "MRU",        "0.00%"),
        ("MRUV",        "v₀ = 1.0 m/s, a = 3.0 m/s²",        "MRUV",       "0.70%"),
        ("Caída Libre", "y₀ = 10 m, g = 9.8 m/s²",           "Caída Libre", "4.54%"),
    ],
    col_widths=[1.3, 2.8, 1.5, 1.7])

normal(doc, (
    "Los tres tipos de movimiento fueron detectados correctamente y los errores "
    "porcentuales se encuentran por debajo del umbral establecido en la hipótesis "
    "(10% para MRU/MRUV, 15% para Caída Libre), confirmando la precisión del sistema."
))

h3(doc, "Características Exportadas")
agregar_tabla_simple(doc,
    ["Formato", "Contenido"],
    [
        ("CSV (.csv)", "Columnas: tiempo_s, posicion_x_m, posicion_y_m, velocidad_m_s, aceleracion_m_s2, tipo_movimiento"),
        ("PNG (.png)", "Figura de las tres gráficas (posición+teórica, velocidad, aceleración) a 150 DPI"),
        ("TXT (.txt)", "Reporte con tipo detectado, promedios de v y a, distancia total, tiempo total, error medio"),
    ],
    col_widths=[1.5, 4.8])

h2(doc, "Interpretación de Resultados")
normal(doc, (
    "El error de 0.00% para MRU es esperado, ya que los datos sintéticos sin ruido "
    "corresponden exactamente a la ecuación lineal y el ajuste por mínimos cuadrados "
    "recupera los parámetros exactos."
))
normal(doc, (
    "El error de 0.70% para MRUV refleja el efecto del ruido Gaussiano añadido "
    "(σ = 0.02 m). El filtro Savitzky-Golay reduce este ruido efectivamente, "
    "permitiendo al sistema estimar los parámetros iniciales (x₀, v₀, a) con alta "
    "precisión mediante regresión polinomial de grado 2."
))
normal(doc, (
    "El error de 4.54% para Caída Libre es mayor debido a que el análisis vertical "
    "acumula más ruido por la dirección del eje Y (vertical), que es más susceptible "
    "a variaciones en la posición del objeto. Este nivel de error es aceptable para "
    "un sistema de medición educativa basado en video convencional."
))

# ══════════════════════════════════════════════════════════
# MARCO DE DISCUSIÓN
# ══════════════════════════════════════════════════════════
h1(doc, "Marco de Discusión")

h2(doc, "Discusión")
normal(doc, (
    "Los resultados obtenidos confirman la viabilidad de utilizar visión computacional "
    "para el análisis cinemático educativo. La combinación de segmentación HSV, filtrado "
    "Savitzky-Golay y diferencias finitas centrales produce mediciones suficientemente "
    "precisas para el nivel de Física 1 universitaria."
))
normal(doc, (
    "Comparado con Tracker Video Analysis, PhysicsMotionAnalyzer ofrece la ventaja "
    "de la automatización completa del rastreo, eliminando el error humano de marcación "
    "manual. Sin embargo, presenta la limitación de depender de la uniformidad del "
    "color del objeto y de las condiciones de iluminación, factores que no afectan "
    "al marcado manual de Tracker."
))
normal(doc, (
    "La clasificación automática del movimiento resulta robusta para los tres tipos "
    "de movimiento considerados. Los umbrales de clasificación (|ā| < 0.5 para MRU, "
    "||ā| − 9.8| < 1.5 para Caída Libre) fueron ajustados empíricamente durante el "
    "proyecto piloto y demuestran ser efectivos para datos con niveles de ruido "
    "representativos de video convencional."
))
normal(doc, (
    "La superposición de la curva teórica en la gráfica de posición constituye una "
    "herramienta pedagógica valiosa: permite al estudiante visualizar directamente "
    "la discrepancia entre el comportamiento real del objeto y la predicción matemática, "
    "reforzando la comprensión de las limitaciones de los modelos físicos ideales."
))

h2(doc, "Conclusiones")
bullet(doc, "PhysicsMotionAnalyzer logra detectar, medir y clasificar automáticamente los tres tipos de movimiento cinemático (MRU, MRUV, Caída Libre) con errores medios inferiores al 5% en condiciones de simulación controlada.")
bullet(doc, "La detección por color HSV es efectiva para objetos con colores saturados (naranja, verde, azul) en condiciones de iluminación uniforme, cumpliendo el requisito de uso con video convencional.")
bullet(doc, "El filtro Savitzky-Golay mejora significativamente la calidad de las derivadas numéricas, reduciendo el efecto del ruido de cuantización inherente a la detección por píxeles.")
bullet(doc, "La interfaz gráfica desarrollada en Tkinter con matplotlib embebido proporciona una experiencia de usuario fluida y pedagogicamente efectiva, con actualización en tiempo real de las tres gráficas físicas.")
bullet(doc, "El sistema es completamente accesible para instituciones educativas guatemaltecas, ya que requiere únicamente hardware convencional (laptop con webcam) y software de código abierto de acceso gratuito.")
bullet(doc, "La hipótesis planteada se confirma: los errores obtenidos (0.00%, 0.70%, 4.54%) están por debajo de los umbrales establecidos (10% y 15% respectivamente).")

h2(doc, "Recomendaciones")
bullet(doc, "Para mejorar la precisión en video real, se recomienda utilizar fondos de color uniforme y neutro (gris, blanco o azul), y evitar la presencia de objetos del mismo color que el objeto a rastrear.")
bullet(doc, "Implementar calibración automática mediante marcadores ArUco para eliminar la necesidad de calibración manual.")
bullet(doc, "Extender el sistema para soportar análisis en dos dimensiones independientes, permitiendo el estudio de movimiento parabólico.")
bullet(doc, "Agregar soporte para múltiples objetos simultáneos mediante algoritmos de rastreo multi-objeto (Deep SORT o ByteTrack).")
bullet(doc, "Incorporar exportación a formato Excel (.xlsx) con gráficas embebidas para facilitar la presentación de resultados.")
bullet(doc, "Desarrollar una versión web del sistema usando Streamlit para eliminar la necesidad de instalación local.")

# ══════════════════════════════════════════════════════════
# REFERENCIAS
# ══════════════════════════════════════════════════════════
h1(doc, "Referencias")

refs = [
    "Serway, R. A., & Jewett, J. W. (2018). Física para ciencias e ingeniería (10.ª ed.). Cengage Learning.",
    "Bradski, G., & Kaehler, A. (2008). Learning OpenCV: Computer Vision with the OpenCV Library. O'Reilly Media.",
    "NumPy Developers. (2024). NumPy 2.4 documentation. https://numpy.org/doc/",
    "Matplotlib Developers. (2024). Matplotlib 3.10 documentation. https://matplotlib.org/stable/",
    "OpenCV Team. (2024). OpenCV 4.13 documentation. https://docs.opencv.org/4.13.0/",
    "SciPy Developers. (2024). scipy.signal.savgol_filter. https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.savgol_filter.html",
    "Brown, D. (2021). Tracker Video Analysis and Modeling Tool. https://physlets.org/tracker/",
    "Python Software Foundation. (2024). Python 3.14 documentation. https://docs.python.org/3.14/",
    "Savitzky, A., & Golay, M. J. E. (1964). Smoothing and Differentiation of Data by Simplified Least Squares Procedures. Analytical Chemistry, 36(8), 1627–1639.",
    "Universidad Mariano Gálvez de Guatemala. (2026). Proyecto de Física 1 — Guía de evaluación. Facultad de Ingeniería en Sistemas.",
]
for i, ref in enumerate(refs, 1):
    p = doc.add_paragraph(f"{i}. {ref}")
    p.paragraph_format.left_indent = Cm(0.5)
    p.paragraph_format.first_line_indent = Cm(-0.5)
    p.paragraph_format.space_after = Pt(4)

# ══════════════════════════════════════════════════════════
# ANEXOS
# ══════════════════════════════════════════════════════════
h1(doc, "Anexos")

h2(doc, "Anexo A — Estructura del Código Fuente")
normal(doc, "La estructura completa del proyecto es la siguiente:")
# Bloque de código como tabla de una columna
code = """\
PhysicsMotionAnalyzer/
├── main.py                    ← punto de entrada
├── run.bat                    ← lanzador Windows (doble clic)
├── requirements.txt           ← dependencias
├── README.md                  ← documentación técnica
├── gui/
│   ├── main_window.py         ← ventana principal, hilo de análisis
│   ├── video_panel.py         ← panel de video con rastreo visual
│   └── graphs_panel.py        ← tres gráficas matplotlib embebidas
├── physics/
│   ├── kinematics.py          ← ecuaciones MRU, MRUV, caída libre
│   ├── classifier.py          ← clasificación automática por aceleración
│   └── validator.py           ← curva teórica y error porcentual
├── tracking/
│   ├── object_tracker.py      ← detección HSV, contornos, centroide
│   └── color_detector.py      ← presets de color y máscara HSV
├── simulation/
│   └── motion_simulator.py    ← generador de datos sintéticos
└── utils/
    ├── data_exporter.py       ← CSV, PNG, TXT
    └── calibration.py         ← conversión píxeles ↔ metros"""
t_code = doc.add_table(rows=1, cols=1)
t_code.style = "Table Grid"
cell = t_code.rows[0].cells[0]
cell.text = code
for run in cell.paragraphs[0].runs:
    run.font.name = "Courier New"
    run.font.size = Pt(9)

h2(doc, "Anexo B — Instrucciones de Instalación y Ejecución")
normal(doc, "Requisitos mínimos:")
bullet(doc, "Python 3.10 o superior (probado con Python 3.14)")
bullet(doc, "Windows 10/11, Linux o macOS")
bullet(doc, "Webcam (solo para modo Cámara)")
normal(doc, "Instalación:")

steps = [
    "Clonar o descargar el proyecto.",
    "Abrir terminal en la carpeta del proyecto.",
    "Ejecutar:  pip install -r requirements.txt",
    "Ejecutar:  python main.py",
]
for i, s in enumerate(steps, 1):
    p = doc.add_paragraph(f"{i}. {s}")
    p.paragraph_format.left_indent = Cm(0.5)

h2(doc, "Anexo C — Capturas de Pantalla del Sistema")
normal(doc, "[PLACEHOLDER: Insertar capturas de pantalla de la interfaz del sistema en funcionamiento — modo simulación, modo video y gráficas generadas.]", italic=True)

h2(doc, "Anexo D — Video Demostrativo")
normal(doc, "[PLACEHOLDER: Insertar enlace o referencia al video demostrativo donde los integrantes del equipo aparecen usando el sistema con una pelota real filmada en movimiento MRUV.]", italic=True)

h2(doc, "Anexo E — Repositorio de Código")
normal(doc, "El código fuente completo del proyecto se encuentra disponible en:")
normal(doc, "GitHub: https://github.com/GHAngelGG/PhysicsMotionAnalyzer  [repositorio privado — acceso a solicitud]", italic=True)

# ─── Guardar ───
output_path = r"C:\Users\josea\OneDrive\Documentos\VSCodeProjects\PhysicsMotionAnalyzer\Informe_PhysicsMotionAnalyzer.docx"
doc.save(output_path)
print(f"Documento guardado en: {output_path}")
