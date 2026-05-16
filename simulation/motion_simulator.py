"""
Simulador de movimiento.

Genera series temporales sintéticas de MRU, MRUV y caída libre para poder
validar los algoritmos sin necesidad de cámara o archivo de video.
"""
import numpy as np

from physics import kinematics


def simular(tipo, x0=0.0, v0=0.0, a=0.0, t_total=5.0, fps=30, ruido=0.0):
    """
    Genera datos simulados de cinemática.

    Parámetros:
        tipo (str): 'MRU', 'MRUV' o 'Caída Libre'.
        x0 (float): posición inicial [m].
        v0 (float): velocidad inicial [m/s].
        a  (float): aceleración [m/s^2] (MRUV).
        t_total (float): duración total [s].
        fps (int): muestras por segundo.
        ruido (float): desviación estándar del ruido gaussiano añadido.

    Retorna:
        dict con:
            t (np.ndarray): vector de tiempos.
            x (np.ndarray): posición horizontal.
            y (np.ndarray): posición vertical.
            signal (np.ndarray): variable principal (x o y según tipo).
            v (np.ndarray): velocidad (derivada numérica).
            a (np.ndarray): aceleración (segunda derivada).
            tipo (str): tipo solicitado.
    """
    n = max(3, int(t_total * fps))
    t = np.linspace(0.0, float(t_total), n)

    if tipo == "MRU":
        x = kinematics.posicion_mru(x0, v0, t)
        y = np.zeros_like(t)
        signal = x
    elif tipo == "Caída Libre":
        # Dejamos x constante y simulamos el eje vertical
        x = np.full_like(t, float(x0))
        y = kinematics.caida_libre(0.0, v0, t, g=kinematics.G)
        signal = y
    else:  # MRUV por defecto
        x = kinematics.posicion_mruv(x0, v0, a, t)
        y = np.zeros_like(t)
        signal = x

    # Ruido gaussiano opcional para simular imprecisiones de cámara
    if ruido > 0:
        rng = np.random.default_rng()
        signal = signal + rng.normal(0.0, ruido, size=signal.shape)
        if tipo == "Caída Libre":
            y = signal
        else:
            x = signal

    v = kinematics.derivada_central(signal, t)
    a_num = kinematics.segunda_derivada(signal, t)

    return {
        "t": t,
        "x": x,
        "y": y,
        "signal": signal,
        "v": v,
        "a": a_num,
        "tipo": tipo,
    }
