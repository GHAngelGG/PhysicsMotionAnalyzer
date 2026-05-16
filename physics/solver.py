"""
Solver de cinemática — despeja la variable faltante en MRU, MRUV y Caída Libre.

Permite al usuario ingresar solo los datos que conoce (mínimo necesario)
y calcula automáticamente la incógnita.

Ejemplos:
    >>> resolver_mru(x0=0, v=2.0, t=5.0)         # → x_final = 10.0
    >>> resolver_mru(x0=0, x_final=10, t=5.0)    # → v = 2.0
    >>> resolver_mruv(x0=0, v0=1, a=2, t=3)      # → x_final = 12.0
    >>> resolver_mruv(x0=0, v0=1, a=2, x_final=12)   # → t = 3.0
    >>> resolver_caida_libre(y0=20, t=2)         # → y_final = 0.4
"""
import math

GRAVEDAD = 9.8  # m/s²


class ErrorSolver(Exception):
    """Error al resolver el sistema (datos insuficientes o incompatibles)."""


# ════════════════════════════════════════════════════════════════════
# MRU — Movimiento Rectilíneo Uniforme
# Ecuación: x_final = x0 + v · t
# Variables: x0, v, t, x_final  →  necesita 3 de 4
# ════════════════════════════════════════════════════════════════════
def resolver_mru(x0=None, v=None, t=None, x_final=None):
    """
    Resuelve la ecuación del MRU (x = x₀ + v·t).
    Requiere exactamente 3 de las 4 variables; calcula la cuarta.

    Retorna:
        dict con las 4 variables resueltas (incluyendo la incógnita)
        y la clave 'incognita' indicando cuál se calculó.
    """
    datos = {"x0": x0, "v": v, "t": t, "x_final": x_final}
    faltantes = [k for k, val in datos.items() if val is None]
    if len(faltantes) != 1:
        raise ErrorSolver(
            f"MRU necesita 3 datos de 4 (x0, v, t, x_final). "
            f"Recibí {4 - len(faltantes)}."
        )
    incognita = faltantes[0]

    if incognita == "x_final":
        datos["x_final"] = x0 + v * t
    elif incognita == "x0":
        datos["x0"] = x_final - v * t
    elif incognita == "v":
        if t == 0:
            raise ErrorSolver("No se puede despejar v si t = 0.")
        datos["v"] = (x_final - x0) / t
    elif incognita == "t":
        if v == 0:
            raise ErrorSolver("No se puede despejar t si v = 0.")
        datos["t"] = (x_final - x0) / v
        if datos["t"] < 0:
            raise ErrorSolver("Los datos dan t negativo (revisá los valores).")

    datos["incognita"] = incognita
    datos["tipo"] = "MRU"
    return datos


# ════════════════════════════════════════════════════════════════════
# MRUV — Movimiento Rectilíneo Uniformemente Variado
# Ecuaciones:
#   (1) x_final = x0 + v0·t + ½·a·t²
#   (2) v_final = v0 + a·t
#   (3) v_final² = v0² + 2·a·(x_final − x0)   [Torricelli]
# Variables: x0, v0, v_final, a, t, x_final  →  necesita 4 de 6 normalmente
# Para simplificar: pedimos al menos x0, v0, a, t  o  podemos despejar t
# ════════════════════════════════════════════════════════════════════
def resolver_mruv(x0=None, v0=None, a=None, t=None, x_final=None,
                  v_final=None):
    """
    Resuelve MRUV. Necesita 4 datos para cerrar el sistema.

    Casos soportados (faltando exactamente UN dato de los 4 base):
      · falta x_final:  x_final = x0 + v0·t + 0.5·a·t²
      · falta x0:       x0 = x_final − v0·t − 0.5·a·t²
      · falta v0:       v0 = (x_final − x0)/t − 0.5·a·t
      · falta a:        a = 2·(x_final − x0 − v0·t) / t²
      · falta t:        cuadrática 0.5·a·t² + v0·t − Δx = 0
      · falta v_final:  v_final = v0 + a·t

    Retorna dict con las variables, además de v_final calculada.
    """
    datos = {"x0": x0, "v0": v0, "a": a, "t": t,
             "x_final": x_final, "v_final": v_final}
    base = ["x0", "v0", "a", "t", "x_final"]
    faltantes = [k for k in base if datos[k] is None]

    if len(faltantes) != 1:
        raise ErrorSolver(
            f"MRUV necesita 4 de 5 variables base "
            f"(x0, v0, a, t, x_final). Recibí "
            f"{5 - len(faltantes)}."
        )
    incognita = faltantes[0]

    if incognita == "x_final":
        datos["x_final"] = x0 + v0 * t + 0.5 * a * t * t
    elif incognita == "x0":
        datos["x0"] = x_final - v0 * t - 0.5 * a * t * t
    elif incognita == "v0":
        if t == 0:
            raise ErrorSolver("No se puede despejar v0 si t = 0.")
        datos["v0"] = (x_final - x0) / t - 0.5 * a * t
    elif incognita == "a":
        if t == 0:
            raise ErrorSolver("No se puede despejar a si t = 0.")
        datos["a"] = 2 * (x_final - x0 - v0 * t) / (t * t)
    elif incognita == "t":
        # 0.5·a·t² + v0·t − (x_final − x0) = 0
        delta_x = x_final - x0
        if abs(a) < 1e-9:
            # Es realmente MRU: x = x0 + v0·t
            if abs(v0) < 1e-9:
                raise ErrorSolver("Con a = 0 y v0 = 0 no hay movimiento.")
            datos["t"] = delta_x / v0
        else:
            A, B, C = 0.5 * a, v0, -delta_x
            disc = B * B - 4 * A * C
            if disc < 0:
                raise ErrorSolver("No hay solución real para t.")
            t1 = (-B + math.sqrt(disc)) / (2 * A)
            t2 = (-B - math.sqrt(disc)) / (2 * A)
            # Elegimos la raíz positiva más chica
            candidatos = [tt for tt in (t1, t2) if tt > 0]
            if not candidatos:
                raise ErrorSolver("Las soluciones de t son negativas.")
            datos["t"] = min(candidatos)

    # Una vez tenemos las 5 base, calculamos v_final
    x0_, v0_, a_, t_, x_f_ = (
        datos["x0"], datos["v0"], datos["a"], datos["t"], datos["x_final"]
    )
    datos["v_final"] = v0_ + a_ * t_
    datos["incognita"] = incognita
    datos["tipo"] = "MRUV"
    return datos


# ════════════════════════════════════════════════════════════════════
# CAÍDA LIBRE
# Ecuación: y_final = y0 + v0·t − ½·g·t²       (g = 9.8 m/s²)
# Variables: y0, v0, t, y_final  →  necesita 3 de 4
# Si v0 = 0 (caída pura desde reposo) y conocés y0 → t = sqrt(2·y0/g)
# ════════════════════════════════════════════════════════════════════
def resolver_caida_libre(y0=None, v0=None, t=None, y_final=None,
                          v_final=None, g=GRAVEDAD):
    """
    Resuelve la caída libre. Requiere 3 datos de 4 (y0, v0, t, y_final).

    Si v0 no se especifica, asume v0 = 0 (caída desde reposo).
    """
    # Si v0 no viene, asumimos 0 (caída desde reposo)
    if v0 is None:
        v0 = 0.0

    datos = {"y0": y0, "v0": v0, "t": t, "y_final": y_final}
    base = ["y0", "v0", "t", "y_final"]
    faltantes = [k for k in base if datos[k] is None]

    if len(faltantes) != 1:
        raise ErrorSolver(
            f"Caída libre necesita 3 de 4 (y0, v0, t, y_final). "
            f"Recibí {4 - len(faltantes)} (v0=0 si lo dejás vacío)."
        )
    incognita = faltantes[0]

    if incognita == "y_final":
        datos["y_final"] = y0 + v0 * t - 0.5 * g * t * t
    elif incognita == "y0":
        datos["y0"] = y_final - v0 * t + 0.5 * g * t * t
    elif incognita == "v0":
        if t == 0:
            raise ErrorSolver("No se puede despejar v0 si t = 0.")
        datos["v0"] = (y_final - y0 + 0.5 * g * t * t) / t
    elif incognita == "t":
        # 0.5·g·t² − v0·t − (y0 − y_final) = 0
        A = -0.5 * g
        B = v0
        C = y0 - y_final
        disc = B * B - 4 * A * C
        if disc < 0:
            raise ErrorSolver("No hay solución real para t.")
        t1 = (-B + math.sqrt(disc)) / (2 * A)
        t2 = (-B - math.sqrt(disc)) / (2 * A)
        candidatos = [tt for tt in (t1, t2) if tt > 0]
        if not candidatos:
            raise ErrorSolver("Las soluciones de t son negativas.")
        datos["t"] = min(candidatos)

    # Calcular v_final
    t_ = datos["t"]
    datos["v_final"] = datos["v0"] - g * t_
    datos["incognita"] = incognita
    datos["tipo"] = "Caída Libre"
    datos["g"] = g
    return datos


# ════════════════════════════════════════════════════════════════════
# Definición de variables que pide cada tipo (para la UI)
# ════════════════════════════════════════════════════════════════════
VARIABLES = {
    "MRU": [
        ("x0",      "x₀  posición inicial",      "m"),
        ("v",       "v   velocidad",              "m/s"),
        ("t",       "t   tiempo total",           "s"),
        ("x_final", "x_f  posición final",        "m"),
    ],
    "MRUV": [
        ("x0",      "x₀   posición inicial",      "m"),
        ("v0",      "v₀   velocidad inicial",     "m/s"),
        ("a",       "a    aceleración",           "m/s²"),
        ("t",       "t    tiempo total",          "s"),
        ("x_final", "x_f  posición final",        "m"),
    ],
    "Caída Libre": [
        ("y0",      "y₀   altura inicial",        "m"),
        ("v0",      "v₀   velocidad inicial (0 = soltada)",  "m/s"),
        ("t",       "t    tiempo total",          "s"),
        ("y_final", "y_f  altura final",          "m"),
    ],
}


def resolver_por_tipo(tipo, datos):
    """
    Despacha al solver correcto según el tipo de movimiento.

    Parámetros:
        tipo (str): 'MRU', 'MRUV' o 'Caída Libre'.
        datos (dict): variables conocidas (las desconocidas son None).
    """
    if tipo == "MRU":
        return resolver_mru(**datos)
    if tipo == "MRUV":
        return resolver_mruv(**datos)
    if tipo == "Caída Libre":
        return resolver_caida_libre(**datos)
    raise ErrorSolver(f"Tipo desconocido: {tipo}")
