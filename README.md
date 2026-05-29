# PhysicsMotionAnalyzer

**Sistema Inteligente de Monitoreo de Movimiento y Análisis Físico en Tiempo Real**

[![Made with Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.13-green.svg)](https://opencv.org/)
[![License](https://img.shields.io/badge/uso-académico-orange.svg)](#licencia)

---

## Versión Web (online)

**Probala desde tu celular o PC sin instalar nada:**

**https://ghangelgg.github.io/PhysicsMotionAnalyzer/**

La versión web tiene 6 modos:
- **Cámara en vivo** — webcam o cámara del celular con detección de color
- **Análisis de Video** — subí un MP4 y analizalo frame por frame
- **Simulador** — generá datos sintéticos con animación
- **Solucionador** — calculadora de cinemática (despeja la incógnita)
- **Validador** — comparar mediciones experimentales contra teoría
- **QR** — generar código QR para compartir el link

---

## Características principales

### Versión escritorio (Python + Tkinter)
- **Tres modos de entrada**: video grabado, cámara en vivo, simulación física
- **Detección de objeto por color HSV** con presets (naranja, rojo, verde, azul, amarillo, magenta) y calibrador visual interactivo
- **Calibrador Visual con lock-on**: click sobre la pelota → fija el color y la sigue específicamente, ignorando otros objetos del mismo color
- **Cálculo en tiempo real** de posición, velocidad y aceleración usando diferencias finitas centrales
- **Clasificación automática** o manual del tipo de movimiento (MRU, MRUV, Caída Libre)
- **Solver de cinemática** que despeja la variable faltante (dejá UN campo vacío)
- **Validación física** contra curva teórica con error porcentual medio
- **Gráficas en vivo** de x(t), v(t) y a(t)
- **Exportación** a CSV, PNG y reporte de texto

### Versión web (HTML + JS puro)
- Sin servidor backend, todo el procesamiento en el navegador
- Detección de color HSV implementada en JavaScript puro (sin OpenCV.js)
- HTTPS automático con GitHub Pages → la cámara funciona en celular
- Generador de QR integrado para compartir en clase

---

## Cómo usar

### Versión web
Abrí la URL en tu celular o PC. Si vas a usar la cámara, dale permiso al navegador.

### Versión escritorio

**Requisitos:**
- Python 3.10+ (probado con Python 3.14)
- Windows / Linux / macOS
- Webcam (opcional, solo para modo cámara)

**Instalación:**
```bash
git clone https://github.com/GHAngelGG/PhysicsMotionAnalyzer.git
cd PhysicsMotionAnalyzer
pip install -r requirements.txt
python main.py
```

En Windows también podés hacer doble click en `run.bat`.

---

## 📐 Ecuaciones implementadas

**MRU** (Movimiento Rectilíneo Uniforme)
```
x(t) = x₀ + v · t
```

**MRUV** (Movimiento Rectilíneo Uniformemente Variado)
```
x(t) = x₀ + v₀ · t + ½ · a · t²
v(t) = v₀ + a · t
v² = v₀² + 2 · a · (x − x₀)    [Torricelli]
```

**Caída Libre** (eje Y positivo hacia arriba, g = 9.8 m/s²)
```
y(t) = y₀ + v₀ · t − ½ · g · t²
```

**Derivadas numéricas** (diferencias finitas centrales)
```
v[i] = (x[i+1] − x[i−1]) / (t[i+1] − t[i−1])
a[i] = (x[i+1] − 2·x[i] + x[i−1]) / Δt²
```

**Clasificación automática**
- MRU si `|ā| < 0.5 m/s²`
- Caída libre si `||ā| − 9.8| < 1.5 m/s²`
- MRUV en cualquier otro caso

---

## Estructura del proyecto

```
PhysicsMotionAnalyzer/
├── main.py                      ← punto de entrada (escritorio)
├── run.bat                      ← lanzador Windows
├── requirements.txt
├── README.md
│
├── docs/                        ← versión web (servida por GitHub Pages)
│   └── index.html
│
├── informe/                     ← documentación académica
│   └── Informe_PhysicsMotionAnalyzer.docx
│
├── tools/                       ← scripts auxiliares
│   ├── generar_documento.py     ← genera el informe Word
│   └── generar_videos_prueba.py ← genera videos sintéticos de prueba
│
├── gui/                         ← interfaz Tkinter
│   ├── main_window.py           ← ventana principal
│   ├── calibrador_visual.py     ← editor visual de color y recorte
│   ├── video_panel.py           ← panel de visualización de video
│   └── graphs_panel.py          ← gráficas matplotlib embebidas
│
├── physics/                     ← cálculos físicos
│   ├── kinematics.py            ← ecuaciones MRU, MRUV, caída libre
│   ├── classifier.py            ← clasificación automática
│   ├── validator.py             ← comparación experimental vs teórico
│   └── solver.py                ← solver inverso (despeja incógnitas)
│
├── tracking/                    ← visión por computadora
│   ├── object_tracker.py        ← rastreador con lock-on
│   └── color_detector.py        ← presets HSV y máscara de color
│
├── simulation/
│   └── motion_simulator.py      ← generador de datos sintéticos
│
└── utils/
    ├── data_exporter.py         ← exportar CSV, PNG, TXT
    └── calibration.py           ← conversión píxeles ↔ metros
```

## Stack técnico

**Escritorio:** Python 3.14 · OpenCV 4.13 · NumPy 2.4 · SciPy 1.17 · Matplotlib 3.10 · Tkinter
**Web:** HTML5 · JavaScript ES2022 · Chart.js · Canvas API · MediaDevices.getUserMedia
**Hosting:** GitHub Pages (gratis, HTTPS, sin servidor backend)

---

