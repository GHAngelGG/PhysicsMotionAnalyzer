"""
Detección por color en espacio HSV.

Define presets comunes (naranja, rojo, verde, azul, amarillo, magenta)
y la función para generar la máscara binaria del objeto.
"""
import cv2
import numpy as np


# Presets HSV aproximados. OpenCV usa H en [0, 179].
# Formato: {nombre: ((h_min, s_min, v_min), (h_max, s_max, v_max))}
PRESETS = {
    "Naranja":  ((5,  120, 120), (20,  255, 255)),
    "Rojo":     ((0,  120, 100), (10,  255, 255)),
    "Verde":    ((40, 70,  70),  (85,  255, 255)),
    "Azul":     ((95, 100, 80),  (130, 255, 255)),
    "Amarillo": ((20, 100, 100), (35,  255, 255)),
    "Magenta":  ((140, 100, 100), (170, 255, 255)),
}


def obtener_preset(nombre):
    """
    Retorna el rango HSV asociado al nombre del preset.

    Parámetros:
        nombre (str): clave del preset ('Naranja', 'Rojo', ...).

    Retorna:
        tuple: (hsv_min, hsv_max) con tuplas de 3 enteros.
    """
    return PRESETS.get(nombre, PRESETS["Naranja"])


def generar_mascara(frame_bgr, hsv_min, hsv_max, blur_ksize=9):
    """
    Convierte un frame BGR a HSV, aplica desenfoque y genera la máscara binaria.

    Parámetros:
        frame_bgr (np.ndarray): frame de OpenCV en BGR.
        hsv_min (tuple): límite inferior HSV (h, s, v).
        hsv_max (tuple): límite superior HSV (h, s, v).
        blur_ksize (int): tamaño del kernel gaussiano (impar).

    Retorna:
        np.ndarray: máscara binaria uint8 (255 donde está el color, 0 fuera).
    """
    if blur_ksize % 2 == 0:
        blur_ksize += 1
    desenfocado = cv2.GaussianBlur(frame_bgr, (blur_ksize, blur_ksize), 0)
    hsv = cv2.cvtColor(desenfocado, cv2.COLOR_BGR2HSV)
    lower = np.array(hsv_min, dtype=np.uint8)
    upper = np.array(hsv_max, dtype=np.uint8)
    mask = cv2.inRange(hsv, lower, upper)
    # Operaciones morfológicas para eliminar ruido
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)
    return mask
