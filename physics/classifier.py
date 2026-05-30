"""
Clasificador automático del tipo de movimiento.

Reglas (en orden de prioridad):
    MRU         : |a_promedio| < umbral_mru  (velocidad ~ constante).
    Caída Libre : movimiento DOMINANTEMENTE vertical Y la aceleración
                  vertical está dentro de un margen amplio de g.
                  Acepta trayectorias con curva leve (no obliga a vertical
                  perfecta) — Jose pidió esa flexibilidad.
    MRUV        : cualquier otra aceleración aproximadamente constante.

`clasificar_movimiento_2d` analiza X e Y por separado para detectar
caída libre incluso cuando el objeto se mueve un poco horizontalmente
(lanzamiento, semi-parabólico). Mantengo la API vieja
`clasificar_movimiento` por retro-compatibilidad.
"""
import numpy as np

from physics import kinematics
from physics.kinematics import G


def clasificar_movimiento(a_array, v_array=None,
                          umbral_mru=0.5, umbral_g=1.5):
    """
    Clasifica el movimiento a partir del vector de aceleraciones (1D).
    API original — usada en módulos viejos.

    Retorna:
        tuple (str, float, float): (tipo, a_promedio, v_promedio)
    """
    if a_array is None or len(a_array) == 0:
        return "Desconocido", 0.0, 0.0

    a = np.asarray(a_array, dtype=float)
    if a.size > 5:
        a_core = a[1:-1]
    else:
        a_core = a
    a_prom = float(np.mean(a_core))

    v_prom = 0.0
    if v_array is not None and len(v_array) > 0:
        v_prom = float(np.mean(np.asarray(v_array, dtype=float)))

    std_a = float(np.std(a_core))

    if abs(a_prom) < umbral_mru and std_a < umbral_mru * 2:
        tipo = "MRU"
    elif abs(abs(a_prom) - G) < umbral_g:
        tipo = "Caída Libre"
    else:
        tipo = "MRUV"

    return tipo, a_prom, v_prom


def clasificar_movimiento_2d(t, x, y, umbral_mru=0.5, umbral_g_amplio=3.5):
    """
    Clasificación 2D inteligente.

    A diferencia de `clasificar_movimiento`, este recibe las DOS coordenadas
    y elige sobre cuál calcular la aceleración (la dominante). Es más
    tolerante con caídas verticales que tengan algo de curva horizontal
    (lanzamiento desde la mano, pelota que rota).

    Algoritmo:
      1) Auto-detecta el tramo activo (descarta reposo).
      2) Calcula a_x y a_y mediante AJUSTE CUADRÁTICO (más robusto que
         derivar dos veces datos ruidosos).
      3) Decide:
         - Si |a_y| ~ g (con margen amplio) y |a_y| >> |a_x| → Caída Libre.
         - Si |a| < umbral_mru → MRU.
         - Si no → MRUV.
      4) Devuelve además una "confianza" (0-1) basada en qué tan cerca de
         g está la aceleración dominante y cuán dominante es la vertical.

    Parámetros:
        t (array-like): tiempos.
        x, y (array-like): posiciones en metros (y POSITIVO hacia arriba).
        umbral_mru (float): umbral de "casi cero" para identificar MRU.
        umbral_g_amplio (float): tolerancia para identificar caída libre
            (por defecto 3.5 m/s²: acepta de 6.3 a 13.3 m/s²).

    Retorna:
        dict con claves:
            tipo (str): "MRU" | "MRUV" | "Caída Libre"
            a_dominante (float): aceleración usada para clasificar
            a_x, a_y (float): aceleraciones en cada eje
            v_prom (float): velocidad promedio (sobre el tramo activo)
            tramo (tuple[int,int]): índices [ini, fin) del tramo activo
            confianza (float): 0..1
    """
    t = np.asarray(t, dtype=float)
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)

    if t.size < 4:
        return {
            "tipo": "Desconocido", "a_dominante": 0.0, "a_x": 0.0, "a_y": 0.0,
            "v_prom": 0.0, "tramo": (0, len(t)), "confianza": 0.0,
        }

    # 1) Tramo activo (descarta reposo)
    ini, fin = kinematics.tramo_activo(t, y, x)
    t_a = t[ini:fin]; x_a = x[ini:fin]; y_a = y[ini:fin]

    # 2) Aceleraciones por ajuste cuadrático
    a_x = kinematics.aceleracion_por_ajuste(t_a, x_a) if len(t_a) >= 3 else 0.0
    a_y = kinematics.aceleracion_por_ajuste(t_a, y_a) if len(t_a) >= 3 else 0.0

    # Velocidad promedio (magnitud)
    if len(t_a) >= 2:
        vx = kinematics.derivada_central(x_a, t_a)
        vy = kinematics.derivada_central(y_a, t_a)
        v_prom = float(np.nanmean(np.sqrt(vx ** 2 + vy ** 2)))
    else:
        v_prom = 0.0

    # 3) Decisión
    # Vertical "dominante": var(y) >> var(x), o |a_y| >> |a_x|
    var_x = float(np.var(x_a)) if len(x_a) > 1 else 0.0
    var_y = float(np.var(y_a)) if len(y_a) > 1 else 0.0
    vertical_dominante = (var_y >= 2.0 * var_x) or (abs(a_y) > 2.5 * abs(a_x))

    err_g = abs(abs(a_y) - G)
    a_total = max(abs(a_x), abs(a_y))

    # Confianza base
    confianza = 0.5
    if a_total < umbral_mru:
        tipo = "MRU"
        a_dom = a_x if abs(a_x) > abs(a_y) else a_y
        confianza = max(0.0, 1.0 - (a_total / max(umbral_mru, 1e-6)))
    elif vertical_dominante and (
        err_g <= umbral_g_amplio          # cerca de g (caso ideal)
        or abs(a_y) > 3.0                  # o caída notable (>3 m/s²),
                                            # aunque la calibración esté
                                            # mal y aún no llegue a g.
                                            # El usuario corregirá con
                                            # auto-calibración.
    ):
        tipo = "Caída Libre"
        a_dom = a_y
        # Confianza: alta si está cerca de g, menor si solo es "vertical sustancial"
        if err_g <= umbral_g_amplio:
            confianza = max(0.3, 1.0 - err_g / umbral_g_amplio)
        else:
            # Vertical pero con calibración dudosa
            confianza = 0.4
    else:
        tipo = "MRUV"
        a_dom = a_y if abs(a_y) > abs(a_x) else a_x
        # Confianza alta si la aceleración es estable y notable
        confianza = min(1.0, abs(a_dom) / max(G, 1e-6))

    return {
        "tipo": tipo,
        "a_dominante": float(a_dom),
        "a_x": float(a_x),
        "a_y": float(a_y),
        "v_prom": float(v_prom),
        "tramo": (int(ini), int(fin)),
        "confianza": float(np.clip(confianza, 0.0, 1.0)),
    }
