"""
Detección por color en espacio HSV.

Soporta presets de un solo rango O presets que "envuelven" por H=0
(p. ej. el rojo cubre H=0-10 y H=165-179). Esto se expresa de forma
simple usando h_min > h_max: si h_min=165 y h_max=10, el detector
arma dos sub-rangos y los une con OR. Así los sliders siguen siendo
una sola tupla (H, S, V) y todo es retro-compatible.
"""
import cv2
import numpy as np


# Presets HSV (OpenCV usa H en [0, 179]).
# Para el ROJO usamos h_min=165, h_max=10 → wrap-around alrededor de H=0.
PRESETS = {
    "Naranja":  ((5,   120, 120), (20,  255, 255)),
    "Rojo":     ((165, 120, 80),  (10,  255, 255)),   # wrap
    "Verde":    ((40,  70,  70),  (85,  255, 255)),
    "Azul":     ((95,  100, 80),  (130, 255, 255)),
    "Amarillo": ((20,  100, 100), (35,  255, 255)),
    "Magenta":  ((140, 100, 100), (170, 255, 255)),
}


def obtener_preset(nombre):
    """
    Retorna el rango HSV asociado al nombre del preset.

    Retorna:
        tuple: (hsv_min, hsv_max).
    """
    return PRESETS.get(nombre, PRESETS["Naranja"])


def generar_mascara(frame_bgr, hsv_min, hsv_max, blur_ksize=9):
    """
    Convierte un frame BGR a HSV, aplica desenfoque y genera la máscara binaria.

    Si h_min > h_max (wrap por H=0, típico del rojo), se calculan DOS sub-rangos
    y se unen con OR. Si no, se procesa como rango simple.

    Parámetros:
        frame_bgr (np.ndarray): frame BGR.
        hsv_min (tuple): (h_min, s_min, v_min).
        hsv_max (tuple): (h_max, s_max, v_max).
        blur_ksize (int): tamaño del kernel gaussiano.

    Retorna:
        np.ndarray: máscara binaria uint8.
    """
    if blur_ksize % 2 == 0:
        blur_ksize += 1
    desenfocado = cv2.GaussianBlur(frame_bgr, (blur_ksize, blur_ksize), 0)
    hsv = cv2.cvtColor(desenfocado, cv2.COLOR_BGR2HSV)

    h_min, s_min, v_min = hsv_min
    h_max, s_max, v_max = hsv_max

    if h_min > h_max:
        # Wrap-around (rojo): unimos [h_min, 179] y [0, h_max]
        lo1 = np.array((h_min, s_min, v_min), dtype=np.uint8)
        hi1 = np.array((179,  s_max, v_max), dtype=np.uint8)
        lo2 = np.array((0,    s_min, v_min), dtype=np.uint8)
        hi2 = np.array((h_max, s_max, v_max), dtype=np.uint8)
        mask = cv2.bitwise_or(cv2.inRange(hsv, lo1, hi1),
                              cv2.inRange(hsv, lo2, hi2))
    else:
        lower = np.array(hsv_min, dtype=np.uint8)
        upper = np.array(hsv_max, dtype=np.uint8)
        mask = cv2.inRange(hsv, lower, upper)

    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)
    return mask
