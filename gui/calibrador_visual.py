"""
Calibrador visual — selección interactiva de color y recorte del video.

Permite al usuario:
  · Navegar el video con un slider de tiempo
  · Hacer clic sobre la pelota → captura su color HSV automáticamente
  · Marcar visualmente el segundo de inicio y fin del análisis
  · Ver en vivo la máscara de detección del color elegido
"""
import tkinter as tk
from tkinter import ttk, messagebox

import cv2
import numpy as np
from PIL import Image, ImageTk


class CalibradorVisual(tk.Toplevel):
    """
    Ventana modal para configurar visualmente el análisis del video.
    """

    # Tolerancia HSV alrededor del pixel clicado
    TOL_H = 10
    TOL_S = 60
    TOL_V = 60

    def __init__(self, master, video_path,
                 hsv_min_inicial, hsv_max_inicial,
                 trim_inicio_actual=0.0, trim_fin_actual=0.0,
                 callback_aplicar=None):
        """
        Parámetros:
            master: ventana padre.
            video_path (str): ruta del video a calibrar.
            hsv_min_inicial, hsv_max_inicial: tuplas (H,S,V) con los rangos previos.
            trim_inicio_actual, trim_fin_actual (float): segundos previos.
            callback_aplicar (callable): función que recibe
                (hsv_min, hsv_max, t_inicio, t_fin) cuando se hace clic en Aplicar.
        """
        super().__init__(master)
        self.title("🎯  Calibrador Visual — Click sobre la pelota")
        self.geometry("1000x780")
        self.minsize(900, 700)
        self.configure(bg="#0f172a")
        self.transient(master)
        self.grab_set()

        # ─── Paleta ───
        self.C_FONDO   = "#0f172a"
        self.C_PANEL   = "#1e293b"
        self.C_BORDE   = "#334155"
        self.C_TEXTO   = "#f1f5f9"
        self.C_TEXTO_2 = "#cbd5e1"
        self.C_GRIS    = "#94a3b8"
        self.C_ACENTO  = "#3b82f6"
        self.C_VERDE   = "#10b981"
        self.C_NARANJA = "#f59e0b"
        self.C_ROJO    = "#ef4444"

        # ─── Estado ───
        self.video_path = video_path
        self.cap = cv2.VideoCapture(video_path)
        if not self.cap.isOpened():
            messagebox.showerror("Calibrador", "No se pudo abrir el video.")
            self.destroy()
            return

        self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 30
        self.n_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.duracion = self.n_frames / self.fps if self.fps > 0 else 0
        self.frame_w = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_h = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # Tamaño de visualización (mantener proporción, máx 720 px de ancho)
        max_w, max_h = 720, 460
        ratio = min(max_w / self.frame_w, max_h / self.frame_h)
        self.disp_w = int(self.frame_w * ratio)
        self.disp_h = int(self.frame_h * ratio)
        self.escala = ratio

        # Variables de calibración (lo que devolveremos)
        self.hsv_min = list(hsv_min_inicial)
        self.hsv_max = list(hsv_max_inicial)
        self.t_inicio = float(trim_inicio_actual)
        self.t_fin    = float(trim_fin_actual) if trim_fin_actual > 0 else self.duracion

        # Lock-on / fijador
        self.posicion_objetivo = None    # (x, y) en coords del frame original
        self.radio_objetivo = 0          # radio detectado del objeto
        self.frame_objetivo_idx = 0      # frame donde se hizo el clic

        self.callback_aplicar = callback_aplicar
        self._frame_actual = None
        self._mostrar_mascara = tk.BooleanVar(value=False)
        self._imgtk = None

        # ─── UI ───
        self._construir_ui()
        self._mostrar_frame_en(0)

    # ──────────────────────────────────────── UI
    def _construir_ui(self):
        # === ENCABEZADO ===
        head = tk.Frame(self, bg=self.C_PANEL, height=64)
        head.pack(side=tk.TOP, fill=tk.X)
        head.pack_propagate(False)
        tk.Label(
            head, text="🎯  Calibrador Visual",
            font=("Segoe UI", 15, "bold"),
            fg=self.C_TEXTO, bg=self.C_PANEL,
        ).pack(side=tk.LEFT, padx=20, pady=12)
        tk.Label(
            head,
            text="Hacé clic sobre el objeto → el sistema captura su color HSV",
            font=("Segoe UI", 9), fg=self.C_TEXTO_2, bg=self.C_PANEL,
        ).pack(side=tk.LEFT, padx=4, pady=12)

        # === PANEL DEL VIDEO ===
        video_wrap = tk.Frame(self, bg=self.C_FONDO)
        video_wrap.pack(side=tk.TOP, padx=16, pady=12)

        canvas_card = tk.Frame(video_wrap, bg=self.C_PANEL, bd=0,
                               highlightbackground=self.C_BORDE,
                               highlightthickness=1)
        canvas_card.pack()
        self.canvas = tk.Canvas(
            canvas_card, width=self.disp_w, height=self.disp_h,
            bg="#000000", highlightthickness=0, cursor="cross",
        )
        self.canvas.pack(padx=2, pady=2)
        self.canvas.bind("<Button-1>", self._on_click_canvas)

        # === BARRA DE NAVEGACIÓN ===
        nav = tk.Frame(self, bg=self.C_FONDO)
        nav.pack(side=tk.TOP, fill=tk.X, padx=16, pady=(0, 6))

        self.var_tiempo = tk.DoubleVar(value=0.0)
        self.lbl_tiempo = tk.Label(
            nav, text="0.00 s  /  0.00 s",
            font=("Consolas", 11, "bold"),
            fg=self.C_TEXTO, bg=self.C_FONDO,
        )
        self.lbl_tiempo.pack(side=tk.LEFT, padx=(4, 8))

        self.scale_tiempo = tk.Scale(
            nav, from_=0, to=max(self.n_frames - 1, 1), orient="horizontal",
            showvalue=False, command=self._on_scale_tiempo,
            bg=self.C_FONDO, fg=self.C_TEXTO_2,
            highlightthickness=0, troughcolor=self.C_PANEL,
            sliderrelief=tk.FLAT, length=600,
        )
        self.scale_tiempo.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # === MARCADORES DE INICIO / FIN ===
        marcas = tk.Frame(self, bg=self.C_FONDO)
        marcas.pack(side=tk.TOP, fill=tk.X, padx=16, pady=(2, 8))

        self.lbl_inicio = tk.Label(
            marcas, text=f"⏵ Inicio: {self.t_inicio:.2f} s",
            font=("Segoe UI", 10, "bold"), fg=self.C_VERDE,
            bg=self.C_PANEL, padx=10, pady=4,
        )
        self.lbl_inicio.pack(side=tk.LEFT, padx=2)
        tk.Button(
            marcas, text="▸ Marcar inicio aquí",
            bg=self.C_VERDE, fg="white", relief=tk.FLAT,
            font=("Segoe UI", 9, "bold"), padx=10, pady=4,
            cursor="hand2", command=self._marcar_inicio,
        ).pack(side=tk.LEFT, padx=4)

        tk.Label(marcas, text="   ", bg=self.C_FONDO).pack(side=tk.LEFT)

        self.lbl_fin = tk.Label(
            marcas, text=f"⏸ Fin: {self.t_fin:.2f} s",
            font=("Segoe UI", 10, "bold"), fg=self.C_ROJO,
            bg=self.C_PANEL, padx=10, pady=4,
        )
        self.lbl_fin.pack(side=tk.LEFT, padx=2)
        tk.Button(
            marcas, text="◂ Marcar fin aquí",
            bg=self.C_ROJO, fg="white", relief=tk.FLAT,
            font=("Segoe UI", 9, "bold"), padx=10, pady=4,
            cursor="hand2", command=self._marcar_fin,
        ).pack(side=tk.LEFT, padx=4)

        # === COLOR CAPTURADO + TOGGLE MÁSCARA ===
        info = tk.Frame(self, bg=self.C_FONDO)
        info.pack(side=tk.TOP, fill=tk.X, padx=16, pady=(0, 8))

        tk.Label(
            info, text="Color HSV capturado:",
            font=("Segoe UI", 9), fg=self.C_TEXTO_2, bg=self.C_FONDO,
        ).pack(side=tk.LEFT, padx=(2, 6))

        self.muestra_color = tk.Label(
            info, text="  ?  ", bg="#444", fg="white",
            font=("Consolas", 11, "bold"), width=4,
        )
        self.muestra_color.pack(side=tk.LEFT, padx=2)

        self.lbl_hsv = tk.Label(
            info,
            text=f"H:[{self.hsv_min[0]}-{self.hsv_max[0]}]  "
                 f"S:[{self.hsv_min[1]}-{self.hsv_max[1]}]  "
                 f"V:[{self.hsv_min[2]}-{self.hsv_max[2]}]",
            font=("Consolas", 9), fg=self.C_TEXTO_2, bg=self.C_FONDO,
        )
        self.lbl_hsv.pack(side=tk.LEFT, padx=8)

        tk.Checkbutton(
            info, text="Mostrar máscara de detección",
            variable=self._mostrar_mascara, command=self._refrescar_frame,
            bg=self.C_FONDO, fg=self.C_TEXTO_2, selectcolor=self.C_PANEL,
            activebackground=self.C_FONDO, activeforeground=self.C_TEXTO,
            font=("Segoe UI", 9),
        ).pack(side=tk.RIGHT, padx=8)

        # === MENSAJE DE INSTRUCCIÓN ===
        self.lbl_msg = tk.Label(
            self,
            text="💡  Movete por el video con el slider, cuando veas la pelota "
                 "claramente hacé CLIC sobre ella para capturar su color.",
            font=("Segoe UI", 9, "italic"), fg=self.C_NARANJA,
            bg=self.C_FONDO, wraplength=900, justify="center",
        )
        self.lbl_msg.pack(side=tk.TOP, pady=(2, 8))

        # === BOTONES INFERIORES ===
        botones = tk.Frame(self, bg=self.C_FONDO)
        botones.pack(side=tk.BOTTOM, fill=tk.X, padx=16, pady=12)

        tk.Button(
            botones, text="✕  Cancelar",
            bg="#475569", fg="white", relief=tk.FLAT,
            font=("Segoe UI", 10, "bold"), padx=18, pady=8,
            cursor="hand2", command=self.destroy,
        ).pack(side=tk.RIGHT, padx=4)

        tk.Button(
            botones, text="✓  Aplicar configuración",
            bg=self.C_ACENTO, fg="white", relief=tk.FLAT,
            font=("Segoe UI", 10, "bold"), padx=18, pady=8,
            cursor="hand2", command=self._aplicar,
        ).pack(side=tk.RIGHT, padx=4)

        tk.Label(
            botones,
            text=f"Video: {self.frame_w}x{self.frame_h}  ·  "
                 f"{self.fps:.1f} fps  ·  {self.duracion:.2f}s",
            font=("Segoe UI", 8), fg=self.C_GRIS, bg=self.C_FONDO,
        ).pack(side=tk.LEFT, padx=4)

    # ──────────────────────────────────────── EVENTOS
    def _on_scale_tiempo(self, _val):
        idx = int(self.scale_tiempo.get())
        self._mostrar_frame_en(idx)

    def _mostrar_frame_en(self, frame_idx):
        try:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ok, frame = self.cap.read()
            if not ok or frame is None:
                return
            self._frame_actual = frame.copy()
            t = frame_idx / self.fps if self.fps > 0 else 0
            self.lbl_tiempo.config(text=f"{t:6.2f} s  /  {self.duracion:.2f} s")
            self._refrescar_frame()
        except Exception as exc:
            print(f"[Calibrador] error: {exc}")

    def _refrescar_frame(self):
        if self._frame_actual is None:
            return
        frame = self._frame_actual.copy()

        # Si está activo el modo máscara, mostrar la detección
        if self._mostrar_mascara.get():
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            mn = np.array(self.hsv_min, dtype=np.uint8)
            mx = np.array(self.hsv_max, dtype=np.uint8)
            mask = cv2.inRange(hsv, mn, mx)
            mask = cv2.erode(mask, None, iterations=2)
            mask = cv2.dilate(mask, None, iterations=2)

            # Buscar contorno mayor
            contornos, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL,
                                            cv2.CHAIN_APPROX_SIMPLE)
            if contornos:
                mayor = max(contornos, key=cv2.contourArea)
                if cv2.contourArea(mayor) > 30:
                    (cx, cy), rad = cv2.minEnclosingCircle(mayor)
                    cv2.circle(frame, (int(cx), int(cy)),
                               int(rad) + 4, (0, 255, 255), 3)
                    cv2.circle(frame, (int(cx), int(cy)), 4,
                               (0, 0, 255), -1)
                    cv2.putText(frame, f"r={int(rad)}px",
                                (int(cx) + 10, int(cy)),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                                (0, 255, 255), 2)
            # Mezcla traslúcida con la máscara
            mask_color = np.zeros_like(frame)
            mask_color[mask > 0] = (255, 200, 0)  # azul clarito en BGR
            frame = cv2.addWeighted(frame, 0.85, mask_color, 0.30, 0)

        # Mostrar el "fijador" (cruz magenta) si hay objetivo
        if self.posicion_objetivo is not None:
            ox, oy = self.posicion_objetivo
            r = max(self.radio_objetivo + 6, 10)
            cv2.circle(frame, (ox, oy), r, (255, 0, 255), 2)
            cv2.line(frame, (ox - r - 10, oy), (ox - r, oy), (255, 0, 255), 2)
            cv2.line(frame, (ox + r, oy), (ox + r + 10, oy), (255, 0, 255), 2)
            cv2.line(frame, (ox, oy - r - 10), (ox, oy - r), (255, 0, 255), 2)
            cv2.line(frame, (ox, oy + r), (ox, oy + r + 10), (255, 0, 255), 2)
            cv2.putText(frame, "OBJETIVO", (ox + r + 12, oy + 4),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 255), 1)

        # Redimensionar para visualización
        disp = cv2.resize(frame, (self.disp_w, self.disp_h))
        rgb = cv2.cvtColor(disp, cv2.COLOR_BGR2RGB)
        self._imgtk = ImageTk.PhotoImage(image=Image.fromarray(rgb))
        self.canvas.delete("frame_img")
        self.canvas.create_image(0, 0, anchor="nw",
                                 image=self._imgtk, tags="frame_img")

    def _on_click_canvas(self, event):
        """
        Captura el color HSV del píxel clicado y FIJA EL OBJETIVO.

        Después del clic:
          1. Toma HSV del parche 5x5 alrededor del clic.
          2. Aplica la máscara y busca el blob más cercano al clic.
          3. Guarda ese blob como objetivo a seguir (posición + radio).
        """
        if self._frame_actual is None:
            return
        # Convertir coordenadas del canvas a coordenadas del frame original
        x = int(event.x / self.escala)
        y = int(event.y / self.escala)
        if x < 0 or y < 0 or x >= self.frame_w or y >= self.frame_h:
            return

        # 1) HSV mediano del parche 5x5
        x1, y1 = max(0, x - 2), max(0, y - 2)
        x2, y2 = min(self.frame_w, x + 3), min(self.frame_h, y + 3)
        parche = self._frame_actual[y1:y2, x1:x2]
        hsv_parche = cv2.cvtColor(parche, cv2.COLOR_BGR2HSV)
        h_med = int(np.median(hsv_parche[:, :, 0]))
        s_med = int(np.median(hsv_parche[:, :, 1]))
        v_med = int(np.median(hsv_parche[:, :, 2]))

        # Rangos HSV con tolerancia
        h_min = max(0,   h_med - self.TOL_H)
        h_max = min(179, h_med + self.TOL_H)
        s_min = max(0,   s_med - self.TOL_S)
        s_max = min(255, s_med + self.TOL_S)
        v_min = max(0,   v_med - self.TOL_V)
        v_max = min(255, v_med + self.TOL_V)
        self.hsv_min = [h_min, s_min, v_min]
        self.hsv_max = [h_max, s_max, v_max]

        # 2) Detectar el blob real más cercano al clic, para fijar objetivo
        hsv = cv2.cvtColor(self._frame_actual, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv,
                           np.array(self.hsv_min, dtype=np.uint8),
                           np.array(self.hsv_max, dtype=np.uint8))
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)
        contornos, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL,
                                        cv2.CHAIN_APPROX_SIMPLE)

        objetivo_x, objetivo_y, radio_obj = x, y, 0
        if contornos:
            # Filtrar por área mínima
            cands = [c for c in contornos if cv2.contourArea(c) >= 30]
            if cands:
                # Elegir el contorno cuyo centro esté más cerca del clic
                def dist_al_click(contorno):
                    M = cv2.moments(contorno)
                    if M["m00"] <= 0:
                        return float("inf")
                    cx = M["m10"] / M["m00"]
                    cy = M["m01"] / M["m00"]
                    return (cx - x) ** 2 + (cy - y) ** 2
                mejor = min(cands, key=dist_al_click)
                M = cv2.moments(mejor)
                if M["m00"] > 0:
                    objetivo_x = int(M["m10"] / M["m00"])
                    objetivo_y = int(M["m01"] / M["m00"])
                    (_, _), r = cv2.minEnclosingCircle(mejor)
                    radio_obj = int(r)

        self.posicion_objetivo = (objetivo_x, objetivo_y)
        self.radio_objetivo = radio_obj
        self.frame_objetivo_idx = int(self.scale_tiempo.get())

        # Actualizar muestra de color
        bgr_med = self._frame_actual[y, x]
        hex_color = f"#{bgr_med[2]:02x}{bgr_med[1]:02x}{bgr_med[0]:02x}"
        self.muestra_color.config(bg=hex_color)
        self.lbl_hsv.config(
            text=f"H:[{h_min}-{h_max}]  "
                 f"S:[{s_min}-{s_max}]  "
                 f"V:[{v_min}-{v_max}]"
        )

        # Mensaje claro
        if radio_obj > 0:
            self.lbl_msg.config(
                text=f"🎯 OBJETIVO FIJADO en ({objetivo_x}, {objetivo_y}) "
                     f"·  radio ≈ {radio_obj} px  ·  El sistema seguirá "
                     f"este objeto durante todo el análisis (modo lock-on).",
                fg=self.C_VERDE,
            )
        else:
            self.lbl_msg.config(
                text=f"⚠ Color capturado en ({x}, {y}), pero no se detectó "
                     f"un blob claro. Probá hacer clic justo en el centro "
                     f"de la pelota.",
                fg=self.C_NARANJA,
            )

        self._mostrar_mascara.set(True)
        self._refrescar_frame()

    def _marcar_inicio(self):
        idx = int(self.scale_tiempo.get())
        self.t_inicio = idx / self.fps
        if self.t_inicio >= self.t_fin:
            self.t_fin = self.duracion
            self.lbl_fin.config(text=f"⏸ Fin: {self.t_fin:.2f} s")
        self.lbl_inicio.config(text=f"⏵ Inicio: {self.t_inicio:.2f} s")

    def _marcar_fin(self):
        idx = int(self.scale_tiempo.get())
        self.t_fin = idx / self.fps
        if self.t_fin <= self.t_inicio:
            messagebox.showwarning(
                "Recorte",
                "El segundo final debe ser mayor que el inicio.",
            )
            return
        self.lbl_fin.config(text=f"⏸ Fin: {self.t_fin:.2f} s")

    def _aplicar(self):
        if self.callback_aplicar is not None:
            self.callback_aplicar(
                tuple(self.hsv_min),
                tuple(self.hsv_max),
                self.t_inicio,
                self.t_fin,
                self.posicion_objetivo,   # (x, y) en coords del frame original
                self.radio_objetivo,      # radio aprox del objeto
            )
        self.cap.release()
        self.destroy()

    def destroy(self):
        try:
            self.cap.release()
        except Exception:
            pass
        super().destroy()
