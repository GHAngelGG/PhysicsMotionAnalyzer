"""
Módulo de cinemática.

Contiene las ecuaciones de movimiento (MRU, MRUV, caída libre) y
funciones para derivación numérica por diferencias finitas.
"""
import numpy as np


# Constante física: aceleración de la gravedad (m/s^2)
G = 9.8


def posicion_mru(x0, v, t):
    """
    Calcula la posición en un Movimiento Rectilíneo Uniforme.

    Ecuación: x(t) = x0 + v * t

    Parámetros:
        x0 (float): posición inicial [m].
        v  (float): velocidad constante [m/s].
        t  (array-like): vector de tiempos [s].

    Retorna:
        np.ndarray: posiciones en cada instante.
    """
    t = np.asarray(t, dtype=float)
    return x0 + v * t


def posicion_mruv(x0, v0, a, t):
    """
    Calcula la posición en un Movimiento Rectilíneo Uniformemente Variado.

    Ecuación: x(t) = x0 + v0 * t + 0.5 * a * t^2

    Parámetros:
        x0 (float): posición inicial [m].
        v0 (float): velocidad inicial [m/s].
        a  (float): aceleración constante [m/s^2].
        t  (array-like): vector de tiempos [s].

    Retorna:
        np.ndarray: posiciones en cada instante.
    """
    t = np.asarray(t, dtype=float)
    return x0 + v0 * t + 0.5 * a * t ** 2


def velocidad_mruv(v0, a, t):
    """
    Velocidad en MRUV: v(t) = v0 + a * t.

    Parámetros:
        v0 (float): velocidad inicial [m/s].
        a  (float): aceleración [m/s^2].
        t  (array-like): tiempos [s].

    Retorna:
        np.ndarray: velocidades.
    """
    t = np.asarray(t, dtype=float)
    return v0 + a * t


def velocidad_torricelli(v0, a, x, x0=0.0):
    """
    Ecuación de Torricelli: v^2 = v0^2 + 2 * a * (x - x0).
    Retorna v (tomando la raíz positiva).
    """
    disc = v0 ** 2 + 2.0 * a * (np.asarray(x) - x0)
    disc = np.clip(disc, 0.0, None)
    return np.sqrt(disc)


def caida_libre(y0, v0, t, g=G):
    """
    Posición vertical en caída libre (eje Y positivo hacia arriba).

    Ecuación: y(t) = y0 + v0 * t - 0.5 * g * t^2

    Parámetros:
        y0 (float): altura inicial [m].
        v0 (float): velocidad inicial vertical [m/s].
        t  (array-like): tiempos [s].
        g  (float): aceleración de la gravedad [m/s^2].

    Retorna:
        np.ndarray: altura en cada instante.
    """
    t = np.asarray(t, dtype=float)
    return y0 + v0 * t - 0.5 * g * t ** 2


def derivada_central(x, t):
    """
    Calcula la primera derivada por diferencias finitas centrales.

    Para puntos interiores:
        v[i] = (x[i+1] - x[i-1]) / (t[i+1] - t[i-1])

    En los extremos se usa diferencia adelantada/atrasada.

    Parámetros:
        x (array-like): serie de posiciones.
        t (array-like): serie de tiempos (misma longitud).

    Retorna:
        np.ndarray: primera derivada (velocidad).
    """
    x = np.asarray(x, dtype=float)
    t = np.asarray(t, dtype=float)
    n = len(x)
    v = np.zeros(n, dtype=float)
    if n < 2:
        return v
    # Extremos: diferencia adelantada / atrasada
    dt0 = t[1] - t[0]
    dtn = t[-1] - t[-2]
    v[0] = (x[1] - x[0]) / dt0 if dt0 != 0 else 0.0
    v[-1] = (x[-1] - x[-2]) / dtn if dtn != 0 else 0.0
    # Puntos interiores
    for i in range(1, n - 1):
        dt = t[i + 1] - t[i - 1]
        if dt == 0:
            continue
        v[i] = (x[i + 1] - x[i - 1]) / dt
    return v


def segunda_derivada(x, t):
    """
    Calcula la segunda derivada por diferencias finitas.

    Para puntos interiores (con paso constante dt):
        a[i] = (x[i+1] - 2*x[i] + x[i-1]) / dt^2

    Parámetros:
        x (array-like): serie de posiciones.
        t (array-like): serie de tiempos.

    Retorna:
        np.ndarray: segunda derivada (aceleración).
    """
    x = np.asarray(x, dtype=float)
    t = np.asarray(t, dtype=float)
    n = len(x)
    a = np.zeros(n, dtype=float)
    if n < 3:
        return a
    for i in range(1, n - 1):
        dt = 0.5 * (t[i + 1] - t[i - 1])
        if dt == 0:
            continue
        a[i] = (x[i + 1] - 2.0 * x[i] + x[i - 1]) / (dt ** 2)
    # Rellenamos extremos copiando para evitar ceros en las gráficas
    a[0] = a[1]
    a[-1] = a[-2]
    return a


def distancia_total(x, y=None):
    """
    Distancia total recorrida a lo largo de una trayectoria.

    Si y es None, calcula en 1D: suma de |Δx|.
    Si se proporciona y, calcula en 2D: suma de sqrt(Δx^2 + Δy^2).

    Retorna:
        float: distancia total en metros.
    """
    x = np.asarray(x, dtype=float)
    if x.size < 2:
        return 0.0
    if y is None:
        return float(np.sum(np.abs(np.diff(x))))
    y = np.asarray(y, dtype=float)
    dx = np.diff(x)
    dy = np.diff(y)
    return float(np.sum(np.sqrt(dx ** 2 + dy ** 2)))


def suavizar(signal, window=5):
    """
    Suaviza una señal 1D. Intenta usar scipy.signal.savgol_filter.
    Si SciPy no está disponible o la ventana es grande, usa media móvil.

    Parámetros:
        signal (array-like): serie de datos.
        window (int): tamaño de la ventana (impar recomendado).

    Retorna:
        np.ndarray: señal suavizada.
    """
    signal = np.asarray(signal, dtype=float)
    if signal.size < 3 or window < 3:
        return signal
    if window % 2 == 0:
        window += 1
    if window > signal.size:
        window = signal.size if signal.size % 2 == 1 else signal.size - 1
        if window < 3:
            return signal
    try:
        from scipy.signal import savgol_filter
        poly = min(3, window - 1)
        return savgol_filter(signal, window, poly)
    except Exception:
        kernel = np.ones(window) / window
        return np.convolve(signal, kernel, mode="same")
