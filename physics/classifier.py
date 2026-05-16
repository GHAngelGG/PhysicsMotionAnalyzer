"""
Clasificador automático del tipo de movimiento.

Reglas:
    MRU         : |a_promedio| < umbral_mru  (velocidad prácticamente constante)
    Caída Libre : |a_promedio ± g| < umbral_g (g = 9.8 m/s^2)
    MRUV        : a_promedio es constante y distinto de cero
"""
import numpy as np

from physics.kinematics import G


def clasificar_movimiento(a_array, v_array=None,
                          umbral_mru=0.5, umbral_g=1.5):
    """
    Clasifica el movimiento a partir del vector de aceleraciones.

    Parámetros:
        a_array (array-like): aceleraciones instantáneas [m/s^2].
        v_array (array-like | None): velocidades (para reportar promedio).
        umbral_mru (float): umbral para considerar aceleración "cero".
        umbral_g   (float): tolerancia para identificar la gravedad.

    Retorna:
        tuple (str, float, float): (tipo, a_promedio, v_promedio)
    """
    if a_array is None or len(a_array) == 0:
        return "Desconocido", 0.0, 0.0

    a = np.asarray(a_array, dtype=float)
    # Ignorar extremos espurios por las diferencias finitas
    if a.size > 5:
        a_core = a[1:-1]
    else:
        a_core = a
    a_prom = float(np.mean(a_core))

    v_prom = 0.0
    if v_array is not None and len(v_array) > 0:
        v_prom = float(np.mean(np.asarray(v_array, dtype=float)))

    # Desviación estándar baja indica aceleración constante
    std_a = float(np.std(a_core))

    if abs(a_prom) < umbral_mru and std_a < umbral_mru * 2:
        tipo = "MRU"
    elif abs(abs(a_prom) - G) < umbral_g:
        tipo = "Caída Libre"
    else:
        tipo = "MRUV"

    return tipo, a_prom, v_prom
