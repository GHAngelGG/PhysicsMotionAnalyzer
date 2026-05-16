"""
Panel con las tres gráficas físicas (posición, velocidad, aceleración).

Utiliza matplotlib embebido en Tkinter mediante FigureCanvasTkAgg.
"""
import tkinter as tk

import matplotlib

matplotlib.use("TkAgg")

from matplotlib.figure import Figure  # noqa: E402
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # noqa: E402


class PanelGraficas(tk.Frame):
    """
    Frame que contiene tres subplots side-by-side:
        ax_x: posición vs tiempo (experimental + teórica)
        ax_v: velocidad vs tiempo
        ax_a: aceleración vs tiempo
    """

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.fig = Figure(figsize=(13, 3.2), dpi=90, facecolor="#ffffff")
        self.ax_x = self.fig.add_subplot(131)
        self.ax_v = self.fig.add_subplot(132)
        self.ax_a = self.fig.add_subplot(133)
        self._configurar_ejes()

        # Línea experimental (azul sólido)
        self.line_x, = self.ax_x.plot([], [], color="#1565c0", linestyle="-",
                                      label="x medido (measured)", linewidth=2)
        # Línea teórica (rojo punteado) — solo en el eje de posición
        self.line_x_teo, = self.ax_x.plot([], [], color="#c62828", linestyle="--",
                                          label="x teórico (theory)", linewidth=1.5, alpha=0.85)
        self.line_v, = self.ax_v.plot([], [], color="#2e7d32", linestyle="-",
                                      label="v(t) m/s", linewidth=2)
        self.line_a, = self.ax_a.plot([], [], color="#ef6c00", linestyle="-",
                                      label="a(t) m/s²", linewidth=2)

        for ax in (self.ax_x, self.ax_v, self.ax_a):
            ax.legend(loc="upper left", fontsize=8)

        self.fig.tight_layout()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def _configurar_ejes(self):
        self.ax_x.set_title("Posición vs Tiempo  ·  Position", fontsize=10, fontweight="bold", color="#1a237e")
        self.ax_x.set_xlabel("Tiempo  t [s]", fontsize=9)
        self.ax_x.set_ylabel("Posición  x [m]", fontsize=9)

        self.ax_v.set_title("Velocidad vs Tiempo  ·  Velocity", fontsize=10, fontweight="bold", color="#1a237e")
        self.ax_v.set_xlabel("Tiempo  t [s]", fontsize=9)
        self.ax_v.set_ylabel("Velocidad  v [m/s]", fontsize=9)

        self.ax_a.set_title("Aceleración vs Tiempo  ·  Acceleration", fontsize=10, fontweight="bold", color="#1a237e")
        self.ax_a.set_xlabel("Tiempo  t [s]", fontsize=9)
        self.ax_a.set_ylabel("Aceleración  a [m/s²]", fontsize=9)

        for ax in (self.ax_x, self.ax_v, self.ax_a):
            ax.grid(True, alpha=0.35, linestyle="--")
            ax.set_facecolor("#fafbfd")
            ax.tick_params(labelsize=8)

    def actualizar(self, t, x, v, a, x_teo=None):
        """
        Actualiza las tres gráficas con nuevas series.

        Parámetros:
            t, x, v, a  (array-like): series experimentales de igual longitud.
            x_teo       (array-like | None): posición teórica para validación visual.
        """
        try:
            self.line_x.set_data(t, x)
            if x_teo is not None and len(x_teo) == len(t):
                self.line_x_teo.set_data(t, x_teo)
            else:
                self.line_x_teo.set_data([], [])
            self.line_v.set_data(t, v)
            self.line_a.set_data(t, a)
            for ax in (self.ax_x, self.ax_v, self.ax_a):
                ax.relim()
                ax.autoscale_view()
            self.canvas.draw_idle()
        except Exception as exc:  # noqa: BLE001
            print(f"[PanelGraficas] error al actualizar: {exc}")

    def limpiar(self):
        """Vacía las tres gráficas."""
        for line in (self.line_x, self.line_x_teo, self.line_v, self.line_a):
            line.set_data([], [])
        for ax in (self.ax_x, self.ax_v, self.ax_a):
            ax.relim()
            ax.autoscale_view()
        self.canvas.draw_idle()
