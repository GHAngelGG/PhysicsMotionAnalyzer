"""
PhysicsMotionAnalyzer - Punto de entrada principal.

Sistema Inteligente de Monitoreo de Movimiento y Análisis Físico en Tiempo Real.
Proyecto universitario de Física 1.

Uso:
    python main.py
"""
import os
import sys
import traceback

# Aseguramos que el directorio raíz del proyecto esté en el PYTHONPATH
# para que los imports relativos al proyecto funcionen al hacer doble clic.
RAIZ = os.path.dirname(os.path.abspath(__file__))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)

from gui.main_window import VentanaPrincipal  # noqa: E402


def main():
    """
    Función principal: instancia la ventana Tkinter y lanza el bucle.

    Retorna:
        int: código de salida (0 = OK, 1 = error).
    """
    try:
        app = VentanaPrincipal()
        app.mainloop()
        return 0
    except Exception as exc:  # noqa: BLE001 - queremos reportar cualquier error fatal
        traceback.print_exc()
        print(f"[ERROR FATAL] {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
