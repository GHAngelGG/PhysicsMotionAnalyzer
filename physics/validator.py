"""
Validación física: compara resultados experimentales con los teóricos.

Reconstruye la curva teórica usando los parámetros iniciales (x0, v0, a)
y calcula el error porcentual promedio y máximo.
"""
import numpy as np

from physics import kinematics


def error_porcentual(exp, teo):
    """
    Calcula el error porcentual entre un valor experimental y uno teórico.

    Fórmula: error% = |exp - teo| / |teo| * 100

    Parámetros:
        exp (float): valor experimental.
        teo (float): valor teórico.

    Retorna:
        float: error en porcentaje. Si |teo| ~ 0, retorna 0 si exp=0, si no inf.
    """
    if abs(teo) < 1e-12:
        return 0.0 if abs(exp) < 1e-12 else float("inf")
    return abs(exp - teo) / abs(teo) * 100.0


def _estimar_parametros(t, x_exp):
    """
    Estima x0, v0 y a a partir de los datos experimentales.
    - x0 = primer valor
    - v0 = diferencia finita en el primer par
    - a  = promedio de la segunda derivada
    """
    t = np.asarray(t, dtype=float)
    x = np.asarray(x_exp, dtype=float)
    x0 = float(x[0])
    if len(x) > 1 and (t[1] - t[0]) != 0:
        v0 = float((x[1] - x[0]) / (t[1] - t[0]))
    else:
        v0 = 0.0
    if len(x) > 3:
        acc = kinematics.segunda_derivada(x, t)
        a = float(np.mean(acc[1:-1]))
    else:
        a = 0.0
    return x0, v0, a


def validar(tipo, t, x_exp, x0=None, v0=None, a=None, g=kinematics.G):
    """
    Compara la serie experimental con la curva teórica correspondiente al tipo.

    Parámetros:
        tipo (str): "MRU", "MRUV" o "Caída Libre".
        t (array-like): tiempos.
        x_exp (array-like): posiciones experimentales.
        x0, v0, a (float | None): parámetros iniciales; si None se estiman.
        g (float): aceleración de la gravedad.

    Retorna:
        dict con claves:
            x_teo (np.ndarray): posición teórica.
            error_medio (float): error % promedio.
            error_max   (float): error % máximo.
            x0, v0, a   (float): parámetros usados.
    """
    t = np.asarray(t, dtype=float)
    x_exp = np.asarray(x_exp, dtype=float)

    x0_e, v0_e, a_e = _estimar_parametros(t, x_exp)
    if x0 is None:
        x0 = x0_e
    if v0 is None:
        v0 = v0_e
    if a is None:
        a = a_e

    if tipo == "MRU":
        x_teo = kinematics.posicion_mru(x0, v0, t)
    elif tipo == "Caída Libre":
        x_teo = kinematics.caida_libre(x0, v0, t, g=g)
    else:  # MRUV u otros
        x_teo = kinematics.posicion_mruv(x0, v0, a, t)

    # Evitamos divisiones por cero usando un pequeño epsilon en el denominador
    eps = 1e-9
    denom = np.where(np.abs(x_teo) > eps, np.abs(x_teo), eps)
    err = np.abs(x_exp - x_teo) / denom * 100.0

    return {
        "x_teo": x_teo,
        "error_medio": float(np.nanmean(err)),
        "error_max": float(np.nanmax(err)),
        "x0": float(x0),
        "v0": float(v0),
        "a": float(a),
    }
