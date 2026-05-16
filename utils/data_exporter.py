"""
Exportación de datos y reportes.

Ofrece:
    - exportar_csv()      -> tabla con tiempo, posición, velocidad, aceleración.
    - exportar_png()      -> guarda la figura de matplotlib en PNG.
    - exportar_reporte()  -> reporte de texto con el resumen experimental.
"""
import datetime

import pandas as pd


def exportar_csv(ruta, t, x, y, v, a, tipo_mov):
    """
    Exporta los datos experimentales a un CSV.

    Columnas:
        tiempo_s, posicion_x_m, posicion_y_m,
        velocidad_m_s, aceleracion_m_s2, tipo_movimiento

    Parámetros:
        ruta (str): ruta del archivo destino.
        t, x, y, v, a (array-like): series con la misma longitud.
        tipo_mov (str): clasificación del movimiento.

    Retorna:
        str: ruta del archivo escrito.
    """
    n = min(len(t), len(x), len(y), len(v), len(a))
    df = pd.DataFrame({
        "tiempo_s": list(t)[:n],
        "posicion_x_m": list(x)[:n],
        "posicion_y_m": list(y)[:n],
        "velocidad_m_s": list(v)[:n],
        "aceleracion_m_s2": list(a)[:n],
        "tipo_movimiento": [tipo_mov] * n,
    })
    df.to_csv(ruta, index=False, encoding="utf-8")
    return ruta


def exportar_png(figura, ruta):
    """
    Guarda una figura de matplotlib como PNG.

    Parámetros:
        figura (matplotlib.figure.Figure): figura a exportar.
        ruta (str): ruta destino (.png).

    Retorna:
        str: ruta del archivo.
    """
    figura.savefig(ruta, dpi=150, bbox_inches="tight")
    return ruta


def exportar_reporte(ruta, resumen):
    """
    Genera un reporte de texto con los resultados del análisis.

    Parámetros:
        ruta (str): ruta del archivo .txt.
        resumen (dict): pares clave/valor con la información a volcar.

    Retorna:
        str: ruta del archivo escrito.
    """
    with open(ruta, "w", encoding="utf-8") as f:
        f.write("==============================================\n")
        f.write(" REPORTE - PhysicsMotionAnalyzer \n")
        f.write(" Proyecto de Física 1 \n")
        f.write("==============================================\n")
        fecha = datetime.datetime.now().isoformat(timespec="seconds")
        f.write(f"Fecha de generación: {fecha}\n\n")
        f.write("-- Resumen de resultados --\n")
        for clave, valor in resumen.items():
            f.write(f"  {clave}: {valor}\n")
        f.write("\nFin del reporte.\n")
    return ruta
