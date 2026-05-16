"""
Panel de video: integra OpenCV con Tkinter mediante Pillow (ImageTk).
"""
import tkinter as tk

import cv2
import numpy as np
from PIL import Image, ImageTk


class PanelVideo(tk.Frame):
    """
    Widget que muestra frames BGR de OpenCV dentro de una ventana Tkinter.

    Atributos:
        ancho (int): ancho fijo de visualización.
        alto  (int): alto  fijo de visualización.
    """

    def __init__(self, master, ancho=720, alto=405, **kwargs):
        """
        Parámetros:
            master: contenedor Tk padre.
            ancho (int): ancho del panel en píxeles.
            alto  (int): alto del panel en píxeles.
        """
        super().__init__(master, bg="black", **kwargs)
        self.ancho = ancho
        self.alto = alto
        self.label = tk.Label(self, bg="black", borderwidth=0)
        self.label.pack(fill=tk.BOTH, expand=True)
        # Mantener referencia para que el garbage collector no la libere
        self._imgtk = None
        self.set_placeholder()

    def set_placeholder(self, texto="Esperando video…", subtexto="Waiting for video"):
        """
        Muestra un fondo negro con un texto informativo.

        Parámetros:
            texto    (str): mensaje principal en español.
            subtexto (str): traducción / subtítulo en inglés.
        """
        frame = np.full((self.alto, self.ancho, 3), 25, dtype=np.uint8)
        # Texto principal centrado
        (tw, th), _ = cv2.getTextSize(texto, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)
        cx = (self.ancho - tw) // 2
        cy = self.alto // 2 - 10
        cv2.putText(frame, texto, (cx, cy),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (220, 220, 220), 2)
        # Sub-texto en inglés
        (tw2, _), _ = cv2.getTextSize(subtexto, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
        cv2.putText(frame, subtexto, ((self.ancho - tw2) // 2, cy + 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (140, 140, 140), 1)
        # Línea decorativa
        cv2.line(frame, (cx, cy + 50), (cx + tw, cy + 50), (60, 80, 110), 2)
        self.mostrar(frame)

    def mostrar(self, frame_bgr):
        """
        Redimensiona y muestra un frame BGR.

        Parámetros:
            frame_bgr (np.ndarray): frame de OpenCV (H, W, 3).
        """
        if frame_bgr is None:
            return
        try:
            frame = cv2.resize(frame_bgr, (self.ancho, self.alto))
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(rgb)
            self._imgtk = ImageTk.PhotoImage(image=img)
            self.label.configure(image=self._imgtk)
        except Exception as exc:  # noqa: BLE001
            print(f"[PanelVideo] error al mostrar frame: {exc}")
