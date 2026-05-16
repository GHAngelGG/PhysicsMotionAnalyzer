"""
Generador de videos sintéticos de prueba para PhysicsMotionAnalyzer.

Crea 3 videos donde una pelota naranja se mueve siguiendo exactamente
las ecuaciones físicas de MRU, MRUV y Caída Libre.

Cada video incluye:
- Pelota naranja saturada (HSV: H~10) con buen contraste
- Fondo blanco limpio (sin objetos del mismo color)
- Una regla métrica visible para calibración
- Resolución HD para detección óptima
"""
import os
import sys
import cv2
import numpy as np

# Forzar UTF-8 en stdout para Windows
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# ─── Parámetros globales ───
ANCHO = 720           # px
ALTO  = 720           # px
FPS   = 60            # frames por segundo
PIX_POR_METRO = 100   # 100 px = 1 m  → calibración fija
RADIO_PELOTA = 22     # px (diámetro 44 px = 44 cm a esta calibración)

# Colores BGR (OpenCV)
COLOR_FONDO   = (245, 245, 245)   # casi blanco
COLOR_PELOTA  = (40, 110, 255)    # naranja saturado (BGR)
COLOR_SOMBRA  = (210, 215, 220)
COLOR_REGLA   = (60, 60, 60)
COLOR_TEXTO   = (40, 40, 60)

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "videos_prueba")
os.makedirs(OUT_DIR, exist_ok=True)


def metros_a_pix(m):
    """Convierte metros a píxeles según la calibración fija."""
    return int(round(m * PIX_POR_METRO))


def dibujar_fondo(frame, etiqueta):
    """Pinta el fondo blanco + regla + etiqueta del modo."""
    frame[:] = COLOR_FONDO
    # Regla horizontal en la parte inferior (cada 10 cm = 10 px)
    y_regla = ALTO - 30
    cv2.line(frame, (10, y_regla), (ANCHO - 10, y_regla), COLOR_REGLA, 2)
    for m in range(0, 8):
        x = 10 + metros_a_pix(m)
        if x < ANCHO - 10:
            cv2.line(frame, (x, y_regla - 8), (x, y_regla + 8), COLOR_REGLA, 2)
            cv2.putText(frame, f"{m}m", (x - 10, y_regla + 24),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, COLOR_REGLA, 1)
    # Regla vertical en el lado izquierdo (para caída libre)
    x_regla = 30
    cv2.line(frame, (x_regla, 10), (x_regla, ALTO - 10), COLOR_REGLA, 2)
    for m in range(0, 8):
        y = 10 + metros_a_pix(m)
        if y < ALTO - 10:
            cv2.line(frame, (x_regla - 8, y), (x_regla + 8, y), COLOR_REGLA, 2)
            cv2.putText(frame, f"{m}m", (x_regla + 12, y + 4),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, COLOR_REGLA, 1)
    # Etiqueta del modo arriba
    cv2.rectangle(frame, (8, 8), (ANCHO - 8, 50), (220, 230, 245), -1)
    cv2.rectangle(frame, (8, 8), (ANCHO - 8, 50), (140, 165, 200), 2)
    cv2.putText(frame, etiqueta, (20, 35),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, COLOR_TEXTO, 2)


def dibujar_pelota(frame, x_px, y_px):
    """Dibuja la pelota con sombra para realismo."""
    # Sombra
    cv2.ellipse(frame, (x_px, ALTO - 25), (RADIO_PELOTA - 4, 6), 0, 0, 360,
                COLOR_SOMBRA, -1)
    # Pelota base
    cv2.circle(frame, (x_px, y_px), RADIO_PELOTA, COLOR_PELOTA, -1)
    # Brillo (highlight) — un círculo más claro arriba a la izquierda
    bx, by = x_px - RADIO_PELOTA // 3, y_px - RADIO_PELOTA // 3
    cv2.circle(frame, (bx, by), RADIO_PELOTA // 4, (180, 200, 255), -1)
    # Borde sutil para destacar contra fondos parecidos
    cv2.circle(frame, (x_px, y_px), RADIO_PELOTA, (20, 70, 180), 2)


def crear_writer(nombre):
    """Crea el VideoWriter MP4."""
    ruta = os.path.join(OUT_DIR, nombre)
    # mp4v es el codec más universal para .mp4 en OpenCV-Windows
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(ruta, fourcc, FPS, (ANCHO, ALTO))
    if not writer.isOpened():
        # Fallback a AVI si MP4 no se puede escribir
        ruta = ruta.replace(".mp4", ".avi")
        fourcc = cv2.VideoWriter_fourcc(*"XVID")
        writer = cv2.VideoWriter(ruta, fourcc, FPS, (ANCHO, ALTO))
    return writer, ruta


# ════════════════════════════════════════════
# 1) MRU — Movimiento Rectilíneo Uniforme
# ════════════════════════════════════════════
def generar_mru():
    """
    Pelota se mueve horizontalmente a velocidad constante.
    v = 1.5 m/s, x va de 0.5 m a 6.5 m → t_total ≈ 4 s
    """
    print("\n[1/3] Generando MRU…")
    v = 1.5         # m/s
    x0 = 0.5        # m (inicio)
    x_max = 6.5     # m (fin)
    t_total = (x_max - x0) / v
    n_frames = int(t_total * FPS)

    writer, ruta = crear_writer("01_MRU.mp4")
    y_fijo = ALTO // 2  # se mueve horizontal a media altura

    for i in range(n_frames):
        t = i / FPS
        x_m = x0 + v * t
        x_px = metros_a_pix(x_m)

        frame = np.zeros((ALTO, ANCHO, 3), dtype=np.uint8)
        dibujar_fondo(frame,
            f"MRU  -  v = {v} m/s constante  -  t = {t:.2f}s")
        dibujar_pelota(frame, x_px, y_fijo)

        # Línea de trayectoria (rastro suave)
        cv2.line(frame, (metros_a_pix(x0), y_fijo), (x_px, y_fijo),
                 (200, 220, 240), 1)

        writer.write(frame)

    writer.release()
    print(f"   ✓ Guardado: {ruta}")
    print(f"   Duración: {t_total:.2f}s | Frames: {n_frames}")
    print(f"   Velocidad teórica: {v} m/s")


# ════════════════════════════════════════════
# 2) MRUV — Movimiento Rectilíneo Uniformemente Variado
# ════════════════════════════════════════════
def generar_mruv():
    """
    Pelota se acelera horizontalmente.
    x₀=0.3 m, v₀=0.5 m/s, a=1.2 m/s², t_total=3 s
    Posición final: 0.3 + 0.5*3 + 0.5*1.2*9 = 7.2 m  → cabe en 7.2 m
    """
    print("\n[2/3] Generando MRUV…")
    x0, v0, a = 0.3, 0.5, 1.2
    t_total = 3.0
    n_frames = int(t_total * FPS)

    writer, ruta = crear_writer("02_MRUV.mp4")
    y_fijo = ALTO // 2

    for i in range(n_frames):
        t = i / FPS
        x_m = x0 + v0 * t + 0.5 * a * t * t
        x_px = metros_a_pix(x_m)

        if x_px > ANCHO - RADIO_PELOTA - 10:
            break

        frame = np.zeros((ALTO, ANCHO, 3), dtype=np.uint8)
        dibujar_fondo(frame,
            f"MRUV  -  a = {a} m/s2 constante  -  t = {t:.2f}s")
        dibujar_pelota(frame, x_px, y_fijo)

        # Rastro
        cv2.line(frame, (metros_a_pix(x0), y_fijo), (x_px, y_fijo),
                 (200, 220, 240), 1)

        writer.write(frame)

    writer.release()
    print(f"   ✓ Guardado: {ruta}")
    print(f"   Duración: {t_total:.2f}s | Frames: {n_frames}")
    print(f"   x0={x0}m, v0={v0}m/s, a={a}m/s² teóricos")


# ════════════════════════════════════════════
# 3) CAÍDA LIBRE
# ════════════════════════════════════════════
def generar_caida_libre():
    """
    Pelota cae desde y₀ alta, g = 9.8 m/s², sin velocidad inicial.
    El frame es de 7.2 m de alto. Usamos y₀ = 6.5 m → cae 6.5 m.
    Tiempo de caída: t = sqrt(2*6.5/9.8) ≈ 1.15 s
    """
    print("\n[3/3] Generando Caída Libre…")
    y0 = 6.5         # altura inicial en metros (medida desde el suelo del frame)
    g = 9.8
    t_total = np.sqrt(2 * y0 / g) + 0.05  # un pelín extra
    n_frames = int(t_total * FPS)

    writer, ruta = crear_writer("03_CaidaLibre.mp4")
    x_fijo = ANCHO // 2  # pelota cae por el centro horizontal

    for i in range(n_frames):
        t = i / FPS
        # Posición desde el suelo (eje Y físico positivo arriba)
        y_fisico = y0 - 0.5 * g * t * t
        if y_fisico < 0:
            y_fisico = 0
        # Convertir a coordenada Y de imagen (origen arriba-izquierda)
        # El "suelo" del frame está en y = ALTO - 40
        suelo_px = ALTO - 40
        y_px = suelo_px - metros_a_pix(y_fisico)

        frame = np.zeros((ALTO, ANCHO, 3), dtype=np.uint8)
        dibujar_fondo(frame,
            f"CAIDA LIBRE  -  g = 9.8 m/s2  -  t = {t:.2f}s")
        dibujar_pelota(frame, x_fijo, y_px)

        # Rastro vertical
        y0_px = suelo_px - metros_a_pix(y0)
        cv2.line(frame, (x_fijo, y0_px), (x_fijo, y_px),
                 (200, 220, 240), 1)

        # Línea del suelo
        cv2.line(frame, (10, suelo_px), (ANCHO - 10, suelo_px),
                 (180, 100, 60), 2)

        writer.write(frame)

        if y_fisico <= 0:
            break

    writer.release()
    print(f"   ✓ Guardado: {ruta}")
    print(f"   Duración: {t_total:.2f}s | Frames: {n_frames}")
    print(f"   y0={y0}m, g={g}m/s² teóricos")


# ────────────────────────────────────────────
def main():
    print("=" * 60)
    print("Generador de videos de prueba — PhysicsMotionAnalyzer")
    print("=" * 60)
    print(f"Resolución:    {ANCHO} x {ALTO}")
    print(f"FPS:           {FPS}")
    print(f"Calibración:   {PIX_POR_METRO} px/m")
    print(f"Carpeta:       {OUT_DIR}")

    generar_mru()
    generar_mruv()
    generar_caida_libre()

    print("\n" + "=" * 60)
    print("✓ LISTO. Los 3 videos están en la carpeta videos_prueba/")
    print("=" * 60)
    print("\nCómo usarlos en la app:")
    print("  1. Abrí la app: python main.py")
    print("  2. Pestaña Video → Cargar archivo de video → elegí uno de los 3")
    print("  3. Preset de color: Naranja")
    print(f"  4. Calibración: {PIX_POR_METRO} px/m  (NO cambies este valor)")
    print("  5. Iniciar")
    print()
    print("Resultados teóricos esperados:")
    print("  - 01_MRU.mp4         → Tipo: MRU,  v=1.5 m/s, a=0")
    print("  - 02_MRUV.mp4        → Tipo: MRUV, v0=0.5 m/s, a=1.2 m/s²")
    print("  - 03_CaidaLibre.mp4  → Tipo: Caída Libre, a=9.8 m/s²")


if __name__ == "__main__":
    main()
