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


def tramo_activo(t, x, y=None, umbral_rel=0.20, umbral_abs=0.30,
                 min_len=5, margen=1):
    """
    Detecta el tramo continuo más largo donde el objeto realmente se mueve.

    Idea: calculamos la velocidad instantánea, fijamos un umbral
    (el mayor entre `umbral_abs` y `umbral_rel * v_max`) y encontramos
    el segmento contiguo más extenso donde |v| supera ese umbral.
    Esto descarta los tramos en reposo (pelota en la mano o en el piso)
    que diluirían el promedio de aceleración.

    Parámetros:
        t (array-like): tiempos [s].
        x (array-like): serie principal (1D, p. ej. la coordenada con
            mayor varianza, típicamente Y para caída libre).
        y (array-like | None): segunda coordenada opcional. Si se da,
            la magnitud de velocidad usa sqrt(vx^2 + vy^2).
        umbral_rel (float): fracción de la velocidad pico que cuenta
            como "movimiento real" (0.2 = 20%).
        umbral_abs (float): umbral mínimo absoluto [m/s] para que
            videos muy lentos no se queden sin tramo.
        min_len (int): número mínimo de muestras del tramo válido.
        margen (int): muestras extra a ambos lados (clipped).

    Retorna:
        tuple (inicio, fin): índices [inicio, fin) del tramo activo.
        Si no se detecta tramo válido, retorna (0, len(t)) — sea, todo.
    """
    t = np.asarray(t, dtype=float)
    x = np.asarray(x, dtype=float)
    if t.size < 4:
        return 0, len(t)

    vx = derivada_central(x, t)
    if y is not None:
        y = np.asarray(y, dtype=float)
        vy = derivada_central(y, t)
        v_mag = np.sqrt(vx ** 2 + vy ** 2)
    else:
        v_mag = np.abs(vx)

    v_max = float(np.nanmax(v_mag)) if v_mag.size else 0.0
    umbral = max(umbral_abs, umbral_rel * v_max)
    activo = v_mag > umbral

    # Run-length: tramo activo más largo
    mejor_ini, mejor_fin, mejor_len = 0, len(t), 0
    i = 0
    while i < len(activo):
        if activo[i]:
            j = i
            while j < len(activo) and activo[j]:
                j += 1
            if j - i > mejor_len:
                mejor_len = j - i
                mejor_ini, mejor_fin = i, j
            i = j
        else:
            i += 1

    if mejor_len < min_len:
        return 0, len(t)

    ini = max(0, mejor_ini - margen)
    fin = min(len(t), mejor_fin + margen)
    return ini, fin


def aceleracion_por_ajuste(t, x):
    """
    Estima la aceleración mediante un ajuste cuadrático
    x(t) ≈ x0 + v0·t + 0.5·a·t².

    Mucho más robusto a ruido que la segunda derivada numérica
    cuando se aplica sobre un tramo limpio (sin reposo).

    Parámetros:
        t (array-like): tiempos [s].
        x (array-like): serie de posiciones [m].

    Retorna:
        float: aceleración estimada [m/s²]. NaN si no hay suficientes
        puntos.
    """
    t = np.asarray(t, dtype=float)
    x = np.asarray(x, dtype=float)
    if t.size < 3 or x.size < 3:
        return float("nan")
    # Centramos el tiempo para mejorar el condicionamiento numérico
    coef = np.polyfit(t - t[0], x, 2)
    return float(2.0 * coef[0])


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
