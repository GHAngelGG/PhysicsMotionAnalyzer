"""
Generador de videos sintéticos de prueba para PhysicsMotionAnalyzer.

Cada video tiene:
- Una pausa al INICIO (pelota quieta) — para practicar recortar
- El movimiento físico real
- Una pausa al FINAL (pelota quieta) — para practicar recortar fin

Especificaciones:
  · Pelota naranja grande (radio 40 px)
  · Fondo blanco limpio (sin objetos del mismo color)
  · Regla métrica en metros para calibración
  · Calibración fija: 80 px/m

Videos generados:
  · 01_MRU.mp4         — 6s total, MRU puro 1s a 5s (4s · ~5m)
  · 02_MRUV.mp4        — 6s total, MRUV puro 1s a 5s (4s · ~7m)
  · 03_CaidaLibre.mp4  — 4s total, caída 1s a 2.1s (1.1s · 6m)
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
ANCHO = 1080          # px (más ancho para MRU/MRUV largos)
ALTO  = 720
FPS   = 30
PIX_POR_METRO = 80    # 80 px = 1 m
RADIO_PELOTA = 40     # px (grande, fácil de detectar)

# Colores BGR (OpenCV)
COLOR_FONDO   = (250, 250, 250)
COLOR_PELOTA  = (40, 110, 255)
COLOR_SOMBRA  = (200, 205, 215)
COLOR_REGLA   = (60, 60, 60)
COLOR_TEXTO   = (40, 40, 60)
COLOR_PAUSA   = (180, 70, 70)
COLOR_ACCION  = (30, 150, 30)

OUT_DIR = os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "videos_prueba"))
os.makedirs(OUT_DIR, exist_ok=True)


def m2px(m):
    return int(round(m * PIX_POR_METRO))


def dibujar_fondo(frame, etiqueta, estado, t_seg):
    """Pinta fondo, reglas y la etiqueta arriba."""
    frame[:] = COLOR_FONDO

    # Regla horizontal en la parte inferior (cada metro)
    y_regla = ALTO - 30
    cv2.line(frame, (10, y_regla), (ANCHO - 10, y_regla), COLOR_REGLA, 2)
    for m in range(0, 14):
        x = 10 + m2px(m)
        if x < ANCHO - 10:
            cv2.line(frame, (x, y_regla - 8), (x, y_regla + 8), COLOR_REGLA, 2)
            cv2.putText(frame, f"{m}m", (x - 12, y_regla + 24),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLOR_REGLA, 1)

    # Regla vertical en el lado izquierdo
    x_regla = 30
    cv2.line(frame, (x_regla, 10), (x_regla, ALTO - 10), COLOR_REGLA, 2)
    for m in range(0, 10):
        y = 10 + m2px(m)
        if y < ALTO - 10:
            cv2.line(frame, (x_regla - 8, y), (x_regla + 8, y), COLOR_REGLA, 2)
            cv2.putText(frame, f"{m}m", (x_regla + 12, y + 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLOR_REGLA, 1)

    # Etiqueta arriba: tipo + tiempo
    cv2.rectangle(frame, (8, 8), (ANCHO - 8, 56), (235, 240, 250), -1)
    cv2.rectangle(frame, (8, 8), (ANCHO - 8, 56), (160, 175, 200), 2)
    cv2.putText(frame, etiqueta, (20, 38),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, COLOR_TEXTO, 2)
    cv2.putText(frame, f"t = {t_seg:5.2f}s", (ANCHO - 240, 38),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, COLOR_TEXTO, 2)

    # Badge de estado
    if estado == "PAUSA":
        cv2.rectangle(frame, (ANCHO - 420, 64), (ANCHO - 250, 96),
                      COLOR_PAUSA, -1)
        cv2.putText(frame, "PAUSA (no analizar)", (ANCHO - 415, 86),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    else:
        cv2.rectangle(frame, (ANCHO - 420, 64), (ANCHO - 240, 96),
                      COLOR_ACCION, -1)
        cv2.putText(frame, "MOVIMIENTO (recortar aqui)", (ANCHO - 415, 86),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)


def dibujar_pelota(frame, x_px, y_px):
    cv2.ellipse(frame, (x_px, ALTO - 27), (RADIO_PELOTA - 8, 8), 0, 0, 360,
                COLOR_SOMBRA, -1)
    cv2.circle(frame, (x_px, y_px), RADIO_PELOTA, COLOR_PELOTA, -1)
    bx, by = x_px - RADIO_PELOTA // 3, y_px - RADIO_PELOTA // 3
    cv2.circle(frame, (bx, by), RADIO_PELOTA // 4, (180, 200, 255), -1)
    cv2.circle(frame, (x_px, y_px), RADIO_PELOTA, (20, 70, 180), 2)


def crear_writer(nombre):
    ruta = os.path.join(OUT_DIR, nombre)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(ruta, fourcc, FPS, (ANCHO, ALTO))
    if not writer.isOpened():
        ruta = ruta.replace(".mp4", ".avi")
        fourcc = cv2.VideoWriter_fourcc(*"XVID")
        writer = cv2.VideoWriter(ruta, fourcc, FPS, (ANCHO, ALTO))
    return writer, ruta


# ════════════════════════════════════════════════════════
# 1) MRU
# ════════════════════════════════════════════════════════
def generar_mru():
    print("\n[1/3] Generando MRU...")
    PAUSA_INI = 1.0
    PAUSA_FIN = 1.0
    DURACION_MOV = 4.0
    v = 1.2
    x0 = 0.5
    x_final = x0 + v * DURACION_MOV

    t_total = PAUSA_INI + DURACION_MOV + PAUSA_FIN
    n_frames = int(t_total * FPS)

    writer, ruta = crear_writer("01_MRU.mp4")
    y_fijo = ALTO // 2

    for i in range(n_frames):
        t = i / FPS
        if t < PAUSA_INI:
            x_m = x0; estado = "PAUSA"
        elif t < PAUSA_INI + DURACION_MOV:
            x_m = x0 + v * (t - PAUSA_INI); estado = "MOV"
        else:
            x_m = x_final; estado = "PAUSA"

        x_px = m2px(x_m)
        frame = np.zeros((ALTO, ANCHO, 3), dtype=np.uint8)
        dibujar_fondo(frame,
            f"MRU  ·  v = {v} m/s constante  ·  Recortar {PAUSA_INI:.1f}s a {PAUSA_INI + DURACION_MOV:.1f}s",
            estado, t)
        dibujar_pelota(frame, x_px, y_fijo)
        writer.write(frame)

    writer.release()
    print(f"   OK: {ruta}")
    print(f"   Total {t_total}s · Recorte sugerido: 1.0s a 5.0s")
    print(f"   Movimiento: v={v}m/s, recorre {x_final-x0:.2f}m en {DURACION_MOV}s")


# ════════════════════════════════════════════════════════
# 2) MRUV
# ════════════════════════════════════════════════════════
def generar_mruv():
    print("\n[2/3] Generando MRUV...")
    PAUSA_INI = 1.0
    PAUSA_FIN = 1.0
    DURACION_MOV = 4.0
    x0 = 0.3; v0 = 0.4; a = 0.7
    x_final = x0 + v0 * DURACION_MOV + 0.5 * a * DURACION_MOV ** 2

    t_total = PAUSA_INI + DURACION_MOV + PAUSA_FIN
    n_frames = int(t_total * FPS)

    writer, ruta = crear_writer("02_MRUV.mp4")
    y_fijo = ALTO // 2

    for i in range(n_frames):
        t = i / FPS
        if t < PAUSA_INI:
            x_m = x0; estado = "PAUSA"
        elif t < PAUSA_INI + DURACION_MOV:
            tt = t - PAUSA_INI
            x_m = x0 + v0 * tt + 0.5 * a * tt ** 2
            estado = "MOV"
        else:
            x_m = x_final; estado = "PAUSA"

        x_px = m2px(x_m)
        if x_px > ANCHO - RADIO_PELOTA - 10:
            x_px = ANCHO - RADIO_PELOTA - 10

        frame = np.zeros((ALTO, ANCHO, 3), dtype=np.uint8)
        dibujar_fondo(frame,
            f"MRUV  ·  v0={v0} m/s, a={a} m/s2  ·  Recortar {PAUSA_INI:.1f}s a {PAUSA_INI + DURACION_MOV:.1f}s",
            estado, t)
        dibujar_pelota(frame, x_px, y_fijo)
        writer.write(frame)

    writer.release()
    print(f"   OK: {ruta}")
    print(f"   Total {t_total}s · Recorte sugerido: 1.0s a 5.0s")
    print(f"   Movimiento: v0={v0}m/s, a={a}m/s2, recorre {x_final-x0:.2f}m")


# ════════════════════════════════════════════════════════
# 3) CAIDA LIBRE
# ════════════════════════════════════════════════════════
def generar_caida_libre():
    print("\n[3/3] Generando Caida Libre...")
    PAUSA_INI = 1.0
    g = 9.8
    y0 = 6.0
    DURACION_CAIDA = np.sqrt(2 * y0 / g)
    PAUSA_FIN = 4.0 - PAUSA_INI - DURACION_CAIDA

    t_total = 4.0
    n_frames = int(t_total * FPS)

    writer, ruta = crear_writer("03_CaidaLibre.mp4")
    x_fijo = ANCHO // 2
    suelo_px = ALTO - 40
    y0_px = suelo_px - m2px(y0)

    for i in range(n_frames):
        t = i / FPS

        if t < PAUSA_INI:
            y_fisico = y0; estado = "PAUSA"
        elif t < PAUSA_INI + DURACION_CAIDA:
            tt = t - PAUSA_INI
            y_fisico = max(0, y0 - 0.5 * g * tt ** 2)
            estado = "MOV"
        else:
            y_fisico = 0; estado = "PAUSA"

        y_px = suelo_px - m2px(y_fisico)

        frame = np.zeros((ALTO, ANCHO, 3), dtype=np.uint8)
        recorte_fin = PAUSA_INI + DURACION_CAIDA
        dibujar_fondo(frame,
            f"CAIDA LIBRE  ·  y0={y0} m, g=9.8 m/s2  ·  Recortar {PAUSA_INI:.1f}s a {recorte_fin:.2f}s",
            estado, t)
        dibujar_pelota(frame, x_fijo, y_px)
        if estado == "MOV":
            cv2.line(frame, (x_fijo, y0_px), (x_fijo, y_px),
                     (200, 220, 240), 2)
        cv2.line(frame, (10, suelo_px), (ANCHO - 10, suelo_px),
                 (140, 80, 50), 3)
        writer.write(frame)

    writer.release()
    print(f"   OK: {ruta}")
    print(f"   Total {t_total}s · Recorte sugerido: 1.00s a {recorte_fin:.2f}s")
    print(f"   Caida pura: y0={y0}m, dura {DURACION_CAIDA:.3f}s")


def main():
    print("=" * 60)
    print("Generador de videos de prueba - PhysicsMotionAnalyzer v2")
    print("=" * 60)
    print(f"Resolucion:    {ANCHO} x {ALTO}")
    print(f"FPS:           {FPS}")
    print(f"Calibracion:   {PIX_POR_METRO} px/m  <- usar este valor en la app")
    print(f"Radio pelota:  {RADIO_PELOTA} px")
    print(f"Carpeta:       {OUT_DIR}")

    generar_mru()
    generar_mruv()
    generar_caida_libre()

    print("\n" + "=" * 60)
    print("LISTO. Videos en: videos_prueba/")
    print("=" * 60)
    print("\nCOMO USARLOS EN LA APP:")
    print(f"  1. Abri la app y elegi modo VIDEO")
    print(f"  2. Calibracion: {PIX_POR_METRO} px/m  (no cambiar)")
    print(f"  3. Preset color: Naranja")
    print()
    print("  Para cada video, recortar SOLO el tramo de movimiento:")
    print("    01_MRU         -> Inicio: 1.0s  ·  Fin: 5.0s")
    print("    02_MRUV        -> Inicio: 1.0s  ·  Fin: 5.0s")
    print("    03_CaidaLibre  -> Inicio: 1.0s  ·  Fin: 2.1s")


if __name__ == "__main__":
    main()
