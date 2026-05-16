"""
Ventana principal de PhysicsMotionAnalyzer — versión simplificada.

Flujo:
  1) Pantalla de bienvenida con 3 botones grandes (Video / Cámara / Simulación).
  2) Una vez elegido el modo, solo se muestran los controles relevantes.
  3) Botón "← Cambiar modo" en la barra superior para volver atrás.
"""
import os
import time
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import cv2
import numpy as np

from gui.video_panel import PanelVideo
from gui.graphs_panel import PanelGraficas
from gui.calibrador_visual import CalibradorVisual
from tracking.object_tracker import RastreadorObjeto
from tracking.color_detector import PRESETS, obtener_preset
from simulation.motion_simulator import simular
from physics import kinematics, classifier, validator
from physics.solver import resolver_por_tipo, ErrorSolver, VARIABLES
from utils.calibration import Calibracion
from utils import data_exporter


class VentanaPrincipal(tk.Tk):
    """Ventana principal con flujo welcome → modo único."""

    # ═══════════════════════════════════════════════════════
    # SETUP
    # ═══════════════════════════════════════════════════════
    def __init__(self):
        super().__init__()
        self.title("PhysicsMotionAnalyzer — Análisis de Movimiento (Física 1)")
        self.geometry("1400x880")
        self.minsize(1000, 640)

        # ─── Paleta moderna ───
        self.C_FONDO     = "#f1f5f9"
        self.C_PANEL     = "#ffffff"
        self.C_SECCION   = "#f8fafc"
        self.C_BORDE     = "#e2e8f0"
        self.C_BORDE_SOFT= "#edf2f7"
        self.C_AZUL      = "#2563eb"
        self.C_AZUL_OSC  = "#1d4ed8"
        self.C_AZUL_LUZ  = "#dbeafe"
        self.C_VERDE     = "#10b981"
        self.C_VERDE_OSC = "#059669"
        self.C_ROJO      = "#ef4444"
        self.C_ROJO_OSC  = "#dc2626"
        self.C_NARANJA   = "#f59e0b"
        self.C_NARANJA_OS= "#d97706"
        self.C_PURPURA   = "#8b5cf6"
        self.C_TEXTO     = "#0f172a"
        self.C_TEXTO_2   = "#334155"
        self.C_GRIS      = "#64748b"
        self.C_GRIS_LUZ  = "#94a3b8"
        self.configure(bg=self.C_FONDO)

        # ─── Estilos ttk ───
        self._configurar_estilos()

        # ─── Estado ───
        self.modo_actual = None    # 'VIDEO', 'CAMARA' o 'SIMULACION'
        self.calib = Calibracion(100.0)
        self.rastreador = RastreadorObjeto()
        self.capturador = None
        self.video_path = None
        self.video_duracion = 0.0
        self.hilo_video = None
        self.ejecutando = False
        self.en_pausa = False
        self.t0 = None

        self.t_list = []
        self.x_list = []
        self.y_list = []
        self._ultimo = None

        # Variables comunes
        self.tipo_movimiento = tk.StringVar(value="MRUV")
        self.color_preset    = tk.StringVar(value="Naranja")
        self.cam_idx         = tk.IntVar(value=0)
        self.ppm             = tk.DoubleVar(value=100.0)
        self.trim_inicio     = tk.DoubleVar(value=0.0)
        self.trim_fin        = tk.DoubleVar(value=0.0)
        # HSV (usado por tracker)
        self.hsv_h_min = tk.IntVar(value=5);   self.hsv_h_max = tk.IntVar(value=20)
        self.hsv_s_min = tk.IntVar(value=120); self.hsv_s_max = tk.IntVar(value=255)
        self.hsv_v_min = tk.IntVar(value=120); self.hsv_v_max = tk.IntVar(value=255)
        # Simulación
        self._sim_vars = {}
        self._sim_check = {}
        self.sim_ruido = tk.DoubleVar(value=0.0)

        # ─── Construcción inicial: welcome screen ───
        self._crear_header()
        self._main_area = tk.Frame(self, bg=self.C_FONDO)
        self._main_area.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self._mostrar_welcome()

        self.protocol("WM_DELETE_WINDOW", self.cerrar)

        # Maximizar
        try:
            self.state("zoomed")
        except Exception:
            pass

    # ─── Estilos ttk ───
    def _configurar_estilos(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure("Modern.TCombobox",
                        fieldbackground="#ffffff", background="#ffffff",
                        foreground=self.C_TEXTO, padding=6)

    # ═══════════════════════════════════════════════════════
    # HEADER (siempre visible)
    # ═══════════════════════════════════════════════════════
    def _crear_header(self):
        head = tk.Frame(self, bg="#0b1220", height=68)
        head.pack(side=tk.TOP, fill=tk.X)
        head.pack_propagate(False)

        # Acento lateral
        tk.Frame(head, bg=self.C_AZUL, width=6).pack(side=tk.LEFT, fill=tk.Y)

        # Logo + título
        izq = tk.Frame(head, bg="#0b1220")
        izq.pack(side=tk.LEFT, padx=18, pady=10)
        tk.Label(izq, text="◉", font=("Segoe UI", 22, "bold"),
                 fg=self.C_AZUL, bg="#0b1220").pack(side=tk.LEFT, padx=(0, 10))
        txt = tk.Frame(izq, bg="#0b1220")
        txt.pack(side=tk.LEFT)
        tk.Label(txt, text="PhysicsMotionAnalyzer",
                 font=("Segoe UI", 16, "bold"),
                 fg="#ffffff", bg="#0b1220").pack(anchor="w")
        self.lbl_modo_actual = tk.Label(
            txt, text="Selección de modo",
            font=("Segoe UI", 9), fg="#94a3b8", bg="#0b1220",
        )
        self.lbl_modo_actual.pack(anchor="w")

        # Botón "Cambiar modo"
        self.btn_cambiar_modo = tk.Button(
            head, text="←  Cambiar modo",
            bg="#1e293b", fg="#cbd5e1",
            activebackground="#334155", activeforeground="#ffffff",
            font=("Segoe UI", 9, "bold"), relief=tk.FLAT, cursor="hand2",
            padx=14, pady=6, command=self._mostrar_welcome,
        )
        self.btn_cambiar_modo.pack(side=tk.RIGHT, padx=14, pady=12)
        self.btn_cambiar_modo.pack_forget()  # oculto en welcome

        # Estado
        estado_box = tk.Frame(head, bg="#1e293b")
        estado_box.pack(side=tk.RIGHT, padx=4, pady=12)
        self.lbl_estado = tk.Label(
            estado_box, text="  ●  Listo  ",
            font=("Segoe UI", 9, "bold"),
            fg=self.C_VERDE, bg="#1e293b", padx=10, pady=6,
        )
        self.lbl_estado.pack()

        # Línea inferior
        tk.Frame(self, bg=self.C_BORDE, height=1).pack(fill=tk.X)

    def _set_estado(self, texto, color=None):
        if color is None:
            color = self.C_VERDE
        try:
            self.lbl_estado.config(text=f"  {texto}  ", fg=color)
        except Exception:
            pass

    # ═══════════════════════════════════════════════════════
    # PANTALLA 1: WELCOME (3 botones grandes)
    # ═══════════════════════════════════════════════════════
    def _mostrar_welcome(self):
        # Detener cualquier análisis activo
        self.ejecutando = False
        if self.capturador is not None:
            try: self.capturador.release()
            except Exception: pass
            self.capturador = None

        # Limpiar área principal
        for w in self._main_area.winfo_children():
            w.destroy()

        self.modo_actual = None
        self.lbl_modo_actual.config(text="Selección de modo")
        self.btn_cambiar_modo.pack_forget()
        self._set_estado("●  Listo", self.C_VERDE)

        # Wrapper centrado
        wrap = tk.Frame(self._main_area, bg=self.C_FONDO)
        wrap.pack(expand=True)

        tk.Label(
            wrap, text="¿Cómo querés analizar el movimiento?",
            font=("Segoe UI", 22, "bold"), fg=self.C_TEXTO, bg=self.C_FONDO,
        ).pack(pady=(40, 8))
        tk.Label(
            wrap, text="How do you want to analyze the motion?",
            font=("Segoe UI", 11, "italic"),
            fg=self.C_GRIS_LUZ, bg=self.C_FONDO,
        ).pack(pady=(0, 36))

        # Grid de 3 tarjetas
        grid = tk.Frame(wrap, bg=self.C_FONDO)
        grid.pack()

        tarjetas = [
            ("📁", "VIDEO", "Analizar un video grabado",
             "Ideal para experimentos repetibles", self.C_AZUL, "VIDEO"),
            ("📷", "CÁMARA", "Capturar en vivo desde la webcam",
             "Tiempo real, requiere webcam", self.C_VERDE, "CAMARA"),
            ("🧪", "SIMULACIÓN", "Generar datos sintéticos",
             "Calculadora física + simulación", self.C_PURPURA, "SIMULACION"),
        ]
        for i, (icono, titulo, desc, sub, color, modo) in enumerate(tarjetas):
            self._tarjeta_modo(grid, icono, titulo, desc, sub, color, modo)\
                .grid(row=0, column=i, padx=18, pady=8)

        # Pie con info
        tk.Label(
            wrap, text="Proyecto Física 1 · Universidad Mariano Gálvez",
            font=("Segoe UI", 8), fg=self.C_GRIS_LUZ, bg=self.C_FONDO,
        ).pack(pady=(40, 8))

    def _tarjeta_modo(self, padre, icono, titulo, desc, sub, color, modo):
        """Tarjeta clickeable de la pantalla de bienvenida."""
        card = tk.Frame(
            padre, bg=self.C_PANEL, bd=0, cursor="hand2",
            highlightbackground=self.C_BORDE, highlightthickness=2,
            width=260, height=300,
        )
        card.pack_propagate(False)

        # Barra superior de color
        tk.Frame(card, bg=color, height=6).pack(fill=tk.X)

        # Contenido
        body = tk.Frame(card, bg=self.C_PANEL)
        body.pack(fill=tk.BOTH, expand=True, padx=20, pady=24)

        tk.Label(body, text=icono, font=("Segoe UI Emoji", 56),
                 bg=self.C_PANEL, fg=color).pack(pady=(0, 10))
        tk.Label(body, text=titulo, font=("Segoe UI", 18, "bold"),
                 fg=self.C_TEXTO, bg=self.C_PANEL).pack()
        tk.Label(body, text=desc, font=("Segoe UI", 10),
                 fg=self.C_TEXTO_2, bg=self.C_PANEL,
                 wraplength=200, justify="center").pack(pady=(8, 4))
        tk.Label(body, text=sub, font=("Segoe UI", 8, "italic"),
                 fg=self.C_GRIS_LUZ, bg=self.C_PANEL,
                 wraplength=200, justify="center").pack()

        # Hover y click
        def on_enter(_):
            card.config(highlightbackground=color, highlightthickness=3)
        def on_leave(_):
            card.config(highlightbackground=self.C_BORDE, highlightthickness=2)
        def on_click(_):
            self._elegir_modo(modo)

        for w in (card, body, *body.winfo_children()):
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)
            w.bind("<Button-1>", on_click)

        return card

    # ═══════════════════════════════════════════════════════
    # ELEGIR MODO → construir el layout específico
    # ═══════════════════════════════════════════════════════
    def _elegir_modo(self, modo):
        self.modo_actual = modo
        self.btn_cambiar_modo.pack(side=tk.RIGHT, padx=14, pady=12)
        self.lbl_modo_actual.config(
            text={"VIDEO": "Modo: Análisis de video",
                  "CAMARA": "Modo: Cámara en vivo",
                  "SIMULACION": "Modo: Simulación física"}[modo]
        )

        # Limpiar y reconstruir el área principal
        for w in self._main_area.winfo_children():
            w.destroy()

        # Layout común: sidebar (izq) + central (der)
        top = tk.Frame(self._main_area, bg=self.C_FONDO)
        top.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Sidebar de controles
        sidebar = tk.Frame(top, bg=self.C_PANEL, width=370,
                           highlightbackground=self.C_BORDE,
                           highlightthickness=1)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(12, 6), pady=12)
        sidebar.pack_propagate(False)

        # Sidebar interno scrolleable
        sb_scroll = tk.Scrollbar(sidebar, orient=tk.VERTICAL)
        sb_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        sb_canvas = tk.Canvas(sidebar, bg=self.C_PANEL,
                              highlightthickness=0,
                              yscrollcommand=sb_scroll.set)
        sb_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb_scroll.config(command=sb_canvas.yview)
        sb_inner = tk.Frame(sb_canvas, bg=self.C_PANEL)
        sb_win = sb_canvas.create_window((0, 0), window=sb_inner, anchor="nw")
        sb_inner.bind("<Configure>",
            lambda e: sb_canvas.configure(scrollregion=sb_canvas.bbox("all")))
        sb_canvas.bind("<Configure>",
            lambda e: sb_canvas.itemconfig(sb_win, width=e.width))
        sb_canvas.bind_all("<MouseWheel>",
            lambda e: sb_canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        # Construir controles según el modo
        if modo == "VIDEO":
            self._construir_sidebar_video(sb_inner)
        elif modo == "CAMARA":
            self._construir_sidebar_camara(sb_inner)
        else:  # SIMULACION
            self._construir_sidebar_simulacion(sb_inner)

        # Centro: video + stats + gráficas (compartido)
        self._construir_area_central(top)

    # ═══════════════════════════════════════════════════════
    # SIDEBAR: MODO VIDEO
    # ═══════════════════════════════════════════════════════
    def _construir_sidebar_video(self, padre):
        self._sidebar_titulo(padre, "📁 Análisis de video", "Video analysis")

        # Paso 1: Cargar video
        self._paso(padre, "1", "Cargá tu video", "Load your video file")
        tk.Button(
            padre, text="📂  Cargar archivo de video…",
            bg=self.C_AZUL, fg="white", relief=tk.FLAT, cursor="hand2",
            font=("Segoe UI", 10, "bold"), pady=10,
            activebackground=self.C_AZUL_OSC, activeforeground="white",
            command=self.cargar_video,
        ).pack(fill=tk.X, padx=16, pady=(4, 4))
        self.lbl_archivo = tk.Label(
            padre, text="(ningún archivo seleccionado)",
            fg=self.C_GRIS_LUZ, wraplength=320, bg=self.C_PANEL,
            justify="left", font=("Segoe UI", 9),
        )
        self.lbl_archivo.pack(fill=tk.X, padx=16, pady=(0, 8))

        # Paso 2: Calibrador
        self._paso(padre, "2", "Fijá el objeto a seguir",
                   "Lock onto the object you want to track")
        self.btn_calibrador = tk.Button(
            padre, text="🎯  Abrir Calibrador Visual",
            bg=self.C_PURPURA, fg="white", relief=tk.FLAT, cursor="hand2",
            font=("Segoe UI", 10, "bold"), pady=10,
            activebackground="#7c3aed", activeforeground="white",
            command=self.abrir_calibrador_visual,
            state="disabled",
        )
        self.btn_calibrador.pack(fill=tk.X, padx=16, pady=(4, 2))
        tk.Label(
            padre,
            text="Click sobre la pelota → fija el color y marca inicio/fin",
            font=("Segoe UI", 8, "italic"),
            fg=self.C_GRIS_LUZ, bg=self.C_PANEL,
            wraplength=320, justify="left",
        ).pack(anchor="w", padx=18, pady=(0, 8))

        # Paso 3: Tipo de movimiento
        self._paso(padre, "3", "Elegí el tipo de movimiento",
                   "Pick the motion type for accurate results")
        self._radios_tipo_movimiento(padre)

        # Paso 4: Calibración (px/m)
        self._paso(padre, "4", "Calibración espacial",
                   "Pixels per meter (optional)")
        cal = tk.Frame(padre, bg=self.C_PANEL)
        cal.pack(fill=tk.X, padx=16, pady=4)
        tk.Label(cal, text="Píxeles por metro:", bg=self.C_PANEL,
                 font=("Segoe UI", 9), fg=self.C_TEXTO_2).pack(side=tk.LEFT)
        tk.Entry(cal, textvariable=self.ppm, width=8,
                 font=("Consolas", 10)).pack(side=tk.LEFT, padx=6)
        tk.Label(cal, text="px/m", bg=self.C_PANEL,
                 fg=self.C_GRIS_LUZ, font=("Segoe UI", 8, "italic")).pack(side=tk.LEFT)
        tk.Label(
            padre, text="💡 Dejá 100 si no estás seguro.",
            font=("Segoe UI", 8), fg=self.C_NARANJA,
            bg=self.C_PANEL,
        ).pack(anchor="w", padx=18, pady=(0, 10))

        # Botones de acción
        self._botones_accion(padre)

    # ═══════════════════════════════════════════════════════
    # SIDEBAR: MODO CÁMARA
    # ═══════════════════════════════════════════════════════
    def _construir_sidebar_camara(self, padre):
        self._sidebar_titulo(padre, "📷 Cámara en vivo", "Live webcam")

        # Paso 1: Cámara
        self._paso(padre, "1", "Seleccioná la cámara", "Select your camera")
        cam = tk.Frame(padre, bg=self.C_PANEL)
        cam.pack(fill=tk.X, padx=16, pady=4)
        tk.Label(cam, text="Índice:", bg=self.C_PANEL,
                 font=("Segoe UI", 9), fg=self.C_TEXTO_2).pack(side=tk.LEFT)
        tk.Spinbox(cam, from_=0, to=5, textvariable=self.cam_idx, width=6,
                   font=("Consolas", 10)).pack(side=tk.LEFT, padx=6)
        tk.Label(cam, text="(0 = webcam integrada)", bg=self.C_PANEL,
                 fg=self.C_GRIS_LUZ, font=("Segoe UI", 8, "italic")
                 ).pack(side=tk.LEFT)

        # Paso 2: Color
        self._paso(padre, "2", "Color del objeto", "Object color")
        col = tk.Frame(padre, bg=self.C_PANEL)
        col.pack(fill=tk.X, padx=16, pady=4)
        tk.Label(col, text="Preset:", bg=self.C_PANEL,
                 font=("Segoe UI", 9), fg=self.C_TEXTO_2).pack(side=tk.LEFT)
        cbo = ttk.Combobox(col, textvariable=self.color_preset,
                           values=list(PRESETS.keys()),
                           state="readonly", width=14,
                           font=("Segoe UI", 10))
        cbo.pack(side=tk.LEFT, padx=6, fill=tk.X, expand=True)
        cbo.bind("<<ComboboxSelected>>", lambda e: self._aplicar_preset())
        # Aplicar el preset inicial
        self._aplicar_preset()

        # Paso 3: Tipo
        self._paso(padre, "3", "Tipo de movimiento", "Motion type")
        self._radios_tipo_movimiento(padre)

        # Paso 4: Calibración
        self._paso(padre, "4", "Calibración (px/m)", "Spatial calibration")
        cal = tk.Frame(padre, bg=self.C_PANEL)
        cal.pack(fill=tk.X, padx=16, pady=4)
        tk.Label(cal, text="Píxeles por metro:", bg=self.C_PANEL,
                 font=("Segoe UI", 9), fg=self.C_TEXTO_2).pack(side=tk.LEFT)
        tk.Entry(cal, textvariable=self.ppm, width=8,
                 font=("Consolas", 10)).pack(side=tk.LEFT, padx=6)

        self._botones_accion(padre)

    # ═══════════════════════════════════════════════════════
    # SIDEBAR: MODO SIMULACIÓN
    # ═══════════════════════════════════════════════════════
    def _construir_sidebar_simulacion(self, padre):
        self._sidebar_titulo(padre, "🧪 Simulación física",
                             "Physics simulator + solver")

        # Paso 1: Tipo
        self._paso(padre, "1", "Tipo de movimiento", "Motion type")
        cbo = ttk.Combobox(padre, textvariable=self.tipo_movimiento,
                           values=["MRU", "MRUV", "Caída Libre"],
                           state="readonly", width=20,
                           font=("Segoe UI", 10))
        cbo.pack(fill=tk.X, padx=16, pady=4)
        cbo.bind("<<ComboboxSelected>>",
                 lambda e: self._reconstruir_campos_sim())

        # Paso 2: Datos
        self._paso(padre, "2", "Ingresá los datos que sepas",
                   "Enter known values · leave ONE empty to solve")
        tk.Label(
            padre,
            text="Marcá  ☐  en la variable que querés que el sistema CALCULE.",
            font=("Segoe UI", 8, "italic"), fg=self.C_NARANJA,
            bg=self.C_PANEL, wraplength=320, justify="left",
        ).pack(anchor="w", padx=18, pady=(0, 4))

        self._sim_campos_frame = tk.Frame(padre, bg=self.C_PANEL)
        self._sim_campos_frame.pack(fill=tk.X, padx=8, pady=4)

        # Ruido (común)
        ruido_row = tk.Frame(padre, bg=self.C_PANEL)
        ruido_row.pack(fill=tk.X, padx=16, pady=(4, 0))
        tk.Label(ruido_row, text="σ ruido:", bg=self.C_PANEL,
                 font=("Segoe UI", 9), fg=self.C_TEXTO_2).pack(side=tk.LEFT)
        tk.Entry(ruido_row, textvariable=self.sim_ruido, width=8,
                 font=("Consolas", 10)).pack(side=tk.LEFT, padx=6)
        tk.Label(ruido_row, text="(0 = sin ruido)", bg=self.C_PANEL,
                 fg=self.C_GRIS_LUZ, font=("Segoe UI", 8, "italic")
                 ).pack(side=tk.LEFT)

        self._lbl_sim_resultado = tk.Label(
            padre, text="", bg=self.C_PANEL,
            font=("Segoe UI", 9, "bold"), fg=self.C_VERDE,
            wraplength=320, justify="left",
        )
        self._lbl_sim_resultado.pack(fill=tk.X, padx=16, pady=(8, 0))

        self._reconstruir_campos_sim()

        self._botones_accion(padre, etiqueta_iniciar="🧮  Calcular y simular")

    # ═══════════════════════════════════════════════════════
    # HELPERS DE CONSTRUCCIÓN DE SIDEBAR
    # ═══════════════════════════════════════════════════════
    def _sidebar_titulo(self, padre, titulo, subtitulo):
        h = tk.Frame(padre, bg=self.C_PANEL)
        h.pack(fill=tk.X, padx=16, pady=(16, 8))
        tk.Label(h, text=titulo, font=("Segoe UI", 14, "bold"),
                 fg=self.C_TEXTO, bg=self.C_PANEL, anchor="w"
                 ).pack(anchor="w")
        tk.Label(h, text=subtitulo, font=("Segoe UI", 9),
                 fg=self.C_GRIS_LUZ, bg=self.C_PANEL, anchor="w"
                 ).pack(anchor="w")
        tk.Frame(padre, bg=self.C_BORDE_SOFT, height=1).pack(
            fill=tk.X, padx=16, pady=(0, 4))

    def _paso(self, padre, num, titulo, subtitulo):
        cont = tk.Frame(padre, bg=self.C_PANEL)
        cont.pack(fill=tk.X, padx=16, pady=(14, 4))
        pill = tk.Label(cont, text=f" PASO {num} ",
                        bg=self.C_AZUL_LUZ, fg=self.C_AZUL_OSC,
                        font=("Segoe UI", 8, "bold"), padx=4, pady=2)
        pill.pack(side=tk.LEFT, padx=(0, 8))
        tx = tk.Frame(cont, bg=self.C_PANEL)
        tx.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Label(tx, text=titulo, font=("Segoe UI", 11, "bold"),
                 fg=self.C_TEXTO, bg=self.C_PANEL, anchor="w"
                 ).pack(anchor="w")
        tk.Label(tx, text=subtitulo, font=("Segoe UI", 8),
                 fg=self.C_GRIS_LUZ, bg=self.C_PANEL, anchor="w"
                 ).pack(anchor="w")

    def _radios_tipo_movimiento(self, padre):
        frm = tk.Frame(padre, bg=self.C_SECCION,
                       highlightbackground=self.C_BORDE, highlightthickness=1)
        frm.pack(fill=tk.X, padx=16, pady=4)
        opciones = [
            ("MRU",         "→  MRU       (velocidad constante)"),
            ("MRUV",        "↗  MRUV     (aceleración constante)"),
            ("Caída Libre", "↓  Caída Libre  (g = 9.8 m/s²)"),
        ]
        for val, txt in opciones:
            tk.Radiobutton(
                frm, text=txt, variable=self.tipo_movimiento, value=val,
                bg=self.C_SECCION, fg=self.C_TEXTO_2,
                activebackground=self.C_SECCION, selectcolor="#ffffff",
                font=("Segoe UI", 9), anchor="w", padx=8, pady=2,
            ).pack(fill=tk.X)

    def _botones_accion(self, padre, etiqueta_iniciar="▶  Iniciar análisis"):
        tk.Frame(padre, bg=self.C_BORDE_SOFT, height=1).pack(
            fill=tk.X, padx=16, pady=(16, 8))

        # Botón principal grande
        self._boton_grande(
            padre, etiqueta_iniciar, self.C_VERDE, self.C_VERDE_OSC,
            self.iniciar, primario=True,
        )
        # Botones secundarios
        grid = tk.Frame(padre, bg=self.C_PANEL)
        grid.pack(fill=tk.X, padx=16, pady=(8, 4))
        grid.grid_columnconfigure(0, weight=1, uniform="b")
        grid.grid_columnconfigure(1, weight=1, uniform="b")
        self._boton_pequeno(grid, "⏸  Pausar", self.C_NARANJA,
                            self.C_NARANJA_OS, self.pausar, 0, 0)
        self._boton_pequeno(grid, "⟳  Reiniciar", self.C_ROJO,
                            self.C_ROJO_OSC, self.reiniciar, 0, 1)
        self._boton_pequeno(grid, "⤓  Exportar CSV", "#475569",
                            "#334155", self.exportar_csv, 1, 0, colspan=2)

    def _boton_grande(self, padre, texto, color, color_hover,
                      cmd, primario=False):
        wrap = tk.Frame(padre, bg=color, cursor="hand2")
        wrap.pack(fill=tk.X, padx=16, pady=4)
        lbl = tk.Label(wrap, text=texto, bg=color, fg="white",
                       font=("Segoe UI", 12, "bold"), pady=12,
                       cursor="hand2")
        lbl.pack(fill=tk.X)
        for w in (wrap, lbl):
            w.bind("<Enter>", lambda _e: (wrap.config(bg=color_hover),
                                          lbl.config(bg=color_hover)))
            w.bind("<Leave>", lambda _e: (wrap.config(bg=color),
                                          lbl.config(bg=color)))
            w.bind("<Button-1>", lambda _e: cmd())

    def _boton_pequeno(self, padre, texto, color, color_hover,
                       cmd, r, c, colspan=1):
        wrap = tk.Frame(padre, bg=color, cursor="hand2")
        wrap.grid(row=r, column=c, columnspan=colspan,
                  sticky="we", padx=2, pady=3)
        lbl = tk.Label(wrap, text=texto, bg=color, fg="white",
                       font=("Segoe UI", 9, "bold"), pady=8, cursor="hand2")
        lbl.pack(fill=tk.X)
        for w in (wrap, lbl):
            w.bind("<Enter>", lambda _e: (wrap.config(bg=color_hover),
                                          lbl.config(bg=color_hover)))
            w.bind("<Leave>", lambda _e: (wrap.config(bg=color),
                                          lbl.config(bg=color)))
            w.bind("<Button-1>", lambda _e: cmd())

    # ═══════════════════════════════════════════════════════
    # ÁREA CENTRAL: Video + Stats + Gráficas
    # ═══════════════════════════════════════════════════════
    def _construir_area_central(self, padre):
        outer = tk.Frame(padre, bg=self.C_FONDO)
        outer.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(6, 12), pady=12)

        # Scroll
        sc = tk.Scrollbar(outer, orient=tk.VERTICAL)
        sc.pack(side=tk.RIGHT, fill=tk.Y)
        canv = tk.Canvas(outer, bg=self.C_FONDO, highlightthickness=0,
                         yscrollcommand=sc.set)
        canv.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sc.config(command=canv.yview)

        inner = tk.Frame(canv, bg=self.C_FONDO)
        win = canv.create_window((0, 0), window=inner, anchor="nw")
        inner.bind("<Configure>",
                   lambda e: canv.configure(scrollregion=canv.bbox("all")))
        canv.bind("<Configure>",
                  lambda e: canv.itemconfig(win, width=e.width))

        # Tarjeta de video (oculta en simulación)
        if self.modo_actual != "SIMULACION":
            v_card = self._tarjeta(inner)
            v_card.pack(fill=tk.X, padx=8, pady=(0, 12))
            self._t_header(v_card, "📹 Vista del video",
                           "Live preview", self.C_AZUL)
            self.panel_video = PanelVideo(v_card, ancho=820, alto=440)
            self.panel_video.pack(padx=14, pady=(0, 14))
        else:
            self.panel_video = None

        # Tarjeta de resultados (KPIs)
        s_card = self._tarjeta(inner)
        s_card.pack(fill=tk.X, padx=8, pady=(0, 12))
        self._t_header(s_card, "📊 Resultados en tiempo real",
                       "Live results", self.C_VERDE)
        self.panel_stats = tk.Frame(s_card, bg=self.C_PANEL)
        self.panel_stats.pack(fill=tk.X, padx=14, pady=(0, 14))
        self._crear_kpis(self.panel_stats)

        # Tarjeta de gráficas (colapsable)
        g_card = self._tarjeta(inner)
        g_card.pack(fill=tk.X, padx=8, pady=(0, 12))
        head = tk.Frame(g_card, bg=self.C_PANEL, cursor="hand2")
        head.pack(fill=tk.X, padx=14, pady=(12, 8))
        tk.Label(head, text="📈", bg=self.C_PURPURA, fg="white",
                 font=("Segoe UI Emoji", 11, "bold"),
                 width=2, height=1).pack(side=tk.LEFT, padx=(0, 10))
        tx = tk.Frame(head, bg=self.C_PANEL); tx.pack(side=tk.LEFT,
                                                       fill=tk.X, expand=True)
        tk.Label(tx, text="Gráficas físicas",
                 font=("Segoe UI", 11, "bold"),
                 fg=self.C_TEXTO, bg=self.C_PANEL, anchor="w").pack(anchor="w")
        tk.Label(tx, text="Posición · Velocidad · Aceleración  (click)",
                 font=("Segoe UI", 8), fg=self.C_GRIS_LUZ,
                 bg=self.C_PANEL, anchor="w").pack(anchor="w")
        self._lbl_toggle_g = tk.Label(
            head, text="▶  Mostrar", bg=self.C_PANEL,
            fg=self.C_AZUL, font=("Segoe UI", 9, "bold"))
        self._lbl_toggle_g.pack(side=tk.RIGHT)
        tk.Frame(g_card, bg=self.C_BORDE_SOFT, height=1).pack(
            fill=tk.X, padx=14)

        self._g_cont = tk.Frame(g_card, bg=self.C_PANEL)
        self.panel_graf = PanelGraficas(self._g_cont, height=320,
                                        bg=self.C_PANEL)
        self.panel_graf.pack(fill=tk.X, padx=14, pady=(8, 14))
        self._g_visible = False

        for w in (head, tx, *tx.winfo_children(), self._lbl_toggle_g):
            w.bind("<Button-1>", lambda e: self._toggle_graf())

    def _toggle_graf(self):
        if self._g_visible:
            self._g_cont.pack_forget()
            self._lbl_toggle_g.config(text="▶  Mostrar")
        else:
            self._g_cont.pack(fill=tk.X)
            self._lbl_toggle_g.config(text="▼  Ocultar")
        self._g_visible = not self._g_visible

    def _tarjeta(self, padre):
        return tk.Frame(padre, bg=self.C_PANEL, bd=0,
                        highlightbackground=self.C_BORDE,
                        highlightthickness=1)

    def _t_header(self, padre, titulo, subtitulo, color):
        head = tk.Frame(padre, bg=self.C_PANEL)
        head.pack(fill=tk.X, padx=14, pady=(12, 6))
        tk.Label(head, text=titulo, font=("Segoe UI", 11, "bold"),
                 fg=self.C_TEXTO, bg=self.C_PANEL, anchor="w"
                 ).pack(side=tk.LEFT)
        tk.Label(head, text="  " + subtitulo, font=("Segoe UI", 9),
                 fg=self.C_GRIS_LUZ, bg=self.C_PANEL, anchor="w"
                 ).pack(side=tk.LEFT)
        tk.Frame(padre, bg=self.C_BORDE_SOFT, height=1).pack(
            fill=tk.X, padx=14, pady=(0, 8))

    def _crear_kpis(self, padre):
        self.var_tipo = tk.StringVar(value="—")
        self.var_vprom = tk.StringVar(value="—")
        self.var_aprom = tk.StringVar(value="—")
        self.var_dist = tk.StringVar(value="—")
        self.var_tiempo = tk.StringVar(value="—")
        self.var_error = tk.StringVar(value="—")
        campos = [
            ("◆", "Tipo de movimiento",   "Motion type",      self.var_tipo,   self.C_AZUL,    ""),
            ("➤", "Velocidad promedio",   "Average speed",    self.var_vprom,  self.C_VERDE,   "m/s"),
            ("⇡", "Aceleración promedio", "Average accel.",   self.var_aprom,  self.C_NARANJA, "m/s²"),
            ("⤢", "Distancia total",      "Total distance",   self.var_dist,   self.C_AZUL,    "m"),
            ("◴", "Tiempo total",         "Total time",       self.var_tiempo, self.C_PURPURA, "s"),
            ("✓", "Error vs teórico",     "Error vs theory",  self.var_error,  self.C_ROJO,    "%"),
        ]
        for i, (icono, lbl_es, lbl_en, var, color, unidad) in enumerate(campos):
            r, c = divmod(i, 3)
            celda = tk.Frame(padre, bg=self.C_PANEL,
                             highlightbackground=self.C_BORDE,
                             highlightthickness=1)
            celda.grid(row=r, column=c, sticky="nsew", padx=5, pady=5)
            padre.grid_columnconfigure(c, weight=1, uniform="kpi")
            tk.Frame(celda, bg=color, height=3).pack(fill=tk.X)
            body = tk.Frame(celda, bg=self.C_PANEL)
            body.pack(fill=tk.BOTH, expand=True, padx=12, pady=10)
            top = tk.Frame(body, bg=self.C_PANEL); top.pack(fill=tk.X)
            tk.Label(top, text=icono, font=("Segoe UI Symbol", 14),
                     fg=color, bg=self.C_PANEL).pack(side=tk.LEFT, padx=(0, 8))
            tx = tk.Frame(top, bg=self.C_PANEL); tx.pack(side=tk.LEFT,
                                                         fill=tk.X, expand=True)
            tk.Label(tx, text=lbl_es, font=("Segoe UI", 9, "bold"),
                     fg=self.C_TEXTO_2, bg=self.C_PANEL, anchor="w"
                     ).pack(anchor="w")
            tk.Label(tx, text=lbl_en, font=("Segoe UI", 8),
                     fg=self.C_GRIS_LUZ, bg=self.C_PANEL, anchor="w"
                     ).pack(anchor="w")
            val = tk.Frame(body, bg=self.C_PANEL); val.pack(fill=tk.X, pady=(8, 0))
            tk.Label(val, textvariable=var, fg=color, bg=self.C_PANEL,
                     font=("Segoe UI", 18, "bold"), anchor="w"
                     ).pack(side=tk.LEFT)
            if unidad:
                tk.Label(val, text=" "+unidad, fg=self.C_GRIS_LUZ,
                         bg=self.C_PANEL, font=("Segoe UI", 10)
                         ).pack(side=tk.LEFT, padx=(2, 0), pady=(8, 0))

    # ═══════════════════════════════════════════════════════
    # SIMULACIÓN: campos dinámicos
    # ═══════════════════════════════════════════════════════
    def _reconstruir_campos_sim(self):
        for w in self._sim_campos_frame.winfo_children():
            w.destroy()
        self._sim_vars.clear()
        self._sim_check.clear()
        self._lbl_sim_resultado.config(text="")

        tipo = self.tipo_movimiento.get()
        for clave, etiq, unidad in VARIABLES.get(tipo, []):
            self._sim_vars[clave] = tk.StringVar(value="")
            self._sim_check[clave] = tk.BooleanVar(value=False)

            row = tk.Frame(self._sim_campos_frame, bg=self.C_PANEL)
            row.pack(fill=tk.X, padx=8, pady=2)
            tk.Checkbutton(
                row, variable=self._sim_check[clave],
                bg=self.C_PANEL, activebackground=self.C_PANEL,
                command=lambda c=clave: self._toggle_calc(c),
            ).pack(side=tk.LEFT)
            tk.Label(row, text=etiq, bg=self.C_PANEL,
                     font=("Segoe UI", 9), fg=self.C_TEXTO,
                     width=24, anchor="w").pack(side=tk.LEFT)
            tk.Entry(row, textvariable=self._sim_vars[clave], width=8,
                     font=("Consolas", 10)).pack(side=tk.LEFT, padx=2)
            tk.Label(row, text=unidad, bg=self.C_PANEL,
                     fg=self.C_GRIS_LUZ, font=("Segoe UI", 8, "italic"),
                     width=5, anchor="w").pack(side=tk.LEFT, padx=2)

    def _toggle_calc(self, clave):
        if self._sim_check[clave].get():
            self._sim_vars[clave].set("")
            for k, v in self._sim_check.items():
                if k != clave:
                    v.set(False)

    # ═══════════════════════════════════════════════════════
    # ACCIONES (compartidas)
    # ═══════════════════════════════════════════════════════
    def _aplicar_preset(self):
        mn, mx = obtener_preset(self.color_preset.get())
        self.hsv_h_min.set(mn[0]); self.hsv_s_min.set(mn[1]); self.hsv_v_min.set(mn[2])
        self.hsv_h_max.set(mx[0]); self.hsv_s_max.set(mx[1]); self.hsv_v_max.set(mx[2])

    def cargar_video(self):
        ruta = filedialog.askopenfilename(
            title="Cargar video",
            filetypes=[("Videos", "*.mp4 *.avi *.mov *.mkv"),
                       ("Todos", "*.*")],
        )
        if not ruta:
            return
        cap_test = cv2.VideoCapture(ruta)
        if not cap_test.isOpened():
            cap_test.release()
            messagebox.showerror("Error de video",
                "OpenCV no puede abrir este archivo.\n"
                "Probá convertirlo a MP4 (H.264).")
            return
        try:
            fps = cap_test.get(cv2.CAP_PROP_FPS) or 30
            nfrm = cap_test.get(cv2.CAP_PROP_FRAME_COUNT) or 0
            self.video_duracion = float(nfrm) / float(fps) if fps > 0 else 0.0
        except Exception:
            self.video_duracion = 0.0
        cap_test.release()

        self.video_path = ruta
        self.lbl_archivo.config(
            text=f"✓ {os.path.basename(ruta)}\n"
                 f"   Duración: {self.video_duracion:.2f}s",
            fg=self.C_AZUL_OSC,
        )
        try:
            self.btn_calibrador.config(state="normal")
        except Exception:
            pass
        self.trim_inicio.set(0.0)
        self.trim_fin.set(0.0)

    def abrir_calibrador_visual(self):
        if not self.video_path:
            messagebox.showinfo("Calibrador", "Primero cargá un video.")
            return
        hsv_min = (self.hsv_h_min.get(), self.hsv_s_min.get(), self.hsv_v_min.get())
        hsv_max = (self.hsv_h_max.get(), self.hsv_s_max.get(), self.hsv_v_max.get())
        try:
            CalibradorVisual(
                self,
                video_path=self.video_path,
                hsv_min_inicial=hsv_min, hsv_max_inicial=hsv_max,
                trim_inicio_actual=self.trim_inicio.get(),
                trim_fin_actual=self.trim_fin.get(),
                callback_aplicar=self._aplicar_calibracion,
            )
        except Exception as exc:
            messagebox.showerror("Calibrador",
                f"No se pudo abrir el calibrador:\n{exc}")

    def _aplicar_calibracion(self, hsv_min, hsv_max, t_inicio, t_fin,
                              objetivo=None, radio_objetivo=0):
        self.hsv_h_min.set(hsv_min[0]); self.hsv_s_min.set(hsv_min[1])
        self.hsv_v_min.set(hsv_min[2])
        self.hsv_h_max.set(hsv_max[0]); self.hsv_s_max.set(hsv_max[1])
        self.hsv_v_max.set(hsv_max[2])
        self.trim_inicio.set(round(t_inicio, 2))
        self.trim_fin.set(round(t_fin, 2))
        if objetivo is not None and objetivo[0] is not None:
            self.rastreador.fijar_objetivo(
                x=objetivo[0], y=objetivo[1],
                radio_referencia=radio_objetivo,
            )
            self._set_estado(f"🎯  Objetivo fijado", "#a78bfa")
        else:
            self._set_estado("✓  Calibración aplicada", self.C_VERDE)

    def iniciar(self):
        if self.ejecutando:
            self.en_pausa = False
            return

        # Reset interno
        self._reset_interno()
        self.ejecutando = True
        self.en_pausa = False

        if self.modo_actual == "SIMULACION":
            self._ejecutar_simulacion()
            self.ejecutando = False
            return

        # Modos VIDEO o CAMARA
        try:
            self.calib.set_ppm(self.ppm.get())
        except Exception:
            self.calib.set_ppm(100.0)

        if not self._abrir_captura():
            self.ejecutando = False
            return

        self.t0 = time.time()
        self._set_estado(f"●  Ejecutando {self.modo_actual}", "#aed581")

        # CAPTURAR los valores Tkinter ahora (el thread no puede leerlos)
        hsv_min = (int(self.hsv_h_min.get()),
                   int(self.hsv_s_min.get()),
                   int(self.hsv_v_min.get()))
        hsv_max = (int(self.hsv_h_max.get()),
                   int(self.hsv_s_max.get()),
                   int(self.hsv_v_max.get()))
        try:
            t_ini = max(0.0, float(self.trim_inicio.get()))
            t_fin = max(0.0, float(self.trim_fin.get()))
        except Exception:
            t_ini, t_fin = 0.0, 0.0
        modo = self.modo_actual

        self.hilo_video = threading.Thread(
            target=self._bucle_video,
            args=(hsv_min, hsv_max, t_ini, t_fin, modo),
            daemon=True,
        )
        self.hilo_video.start()

    def pausar(self):
        if self.ejecutando:
            self.en_pausa = not self.en_pausa
            self._set_estado("⏸  En pausa" if self.en_pausa else "●  Analizando…",
                             "#ffd54f" if self.en_pausa else "#aed581")

    def reiniciar(self):
        self._reset_interno()
        self._set_estado("●  Listo", self.C_VERDE)

    def _reset_interno(self):
        self.ejecutando = False
        self.en_pausa = False
        if self.capturador is not None:
            try: self.capturador.release()
            except Exception: pass
            self.capturador = None
        # Mantener objetivo fijado del calibrador
        self.rastreador.reiniciar(mantener_objetivo=True)
        self.t_list.clear(); self.x_list.clear(); self.y_list.clear()
        self._ultimo = None
        try:
            self.panel_graf.limpiar()
        except Exception:
            pass
        try:
            if self.panel_video:
                self.panel_video.set_placeholder()
        except Exception:
            pass
        for v in (self.var_tipo, self.var_vprom, self.var_aprom,
                  self.var_dist, self.var_tiempo, self.var_error):
            try: v.set("—")
            except Exception: pass

    def cerrar(self):
        self.ejecutando = False
        try:
            if self.capturador: self.capturador.release()
        except Exception: pass
        self.after(150, self.destroy)

    # ─── CAPTURA / TRACKING ───
    def _abrir_captura(self):
        try:
            if self.modo_actual == "VIDEO":
                if not self.video_path:
                    messagebox.showwarning("Video", "Primero cargá un video.")
                    return False
                self.capturador = cv2.VideoCapture(self.video_path)
            else:  # CAMARA
                self.capturador = cv2.VideoCapture(int(self.cam_idx.get()),
                                                    cv2.CAP_DSHOW)
            if not self.capturador.isOpened():
                messagebox.showerror("Error", "No se pudo abrir la fuente de video.")
                self.capturador = None
                return False
            return True
        except Exception as exc:
            messagebox.showerror("Error", f"Falla al abrir captura: {exc}")
            self.capturador = None
            return False

    def _bucle_video(self, hsv_min, hsv_max, t_ini, t_fin, modo):
        try:
            fps_video = self.capturador.get(cv2.CAP_PROP_FPS) or 30
        except Exception:
            fps_video = 30
        dt_target = 1.0 / max(15.0, min(30.0, fps_video))

        # Aplicar el inicio del trim (saltar al segundo de inicio)
        if modo == "VIDEO" and t_ini > 0:
            try:
                self.capturador.set(cv2.CAP_PROP_POS_MSEC, t_ini * 1000.0)
            except Exception:
                pass

        while self.ejecutando and self.capturador is not None:
            if self.en_pausa:
                time.sleep(0.05); continue

            t_inicio = time.time()
            try:
                ok, frame = self.capturador.read()
            except Exception:
                break
            if not ok or frame is None:
                break

            if modo == "VIDEO" and t_fin > 0:
                try:
                    pos_ms = self.capturador.get(cv2.CAP_PROP_POS_MSEC)
                    if pos_ms / 1000.0 >= t_fin:
                        break
                except Exception:
                    pass

            try:
                centro, _r, _m, anotado = self.rastreador.procesar(
                    frame, hsv_min, hsv_max)
            except Exception as exc:
                print(f"[tracking] {exc}")
                anotado = frame; centro = None

            if centro is not None:
                t_rel = time.time() - self.t0
                h = frame.shape[0]
                xm = float(self.calib.pix_a_m(centro[0]))
                ym = float(self.calib.pix_a_m(h - centro[1]))
                self.t_list.append(t_rel)
                self.x_list.append(xm); self.y_list.append(ym)

            self.after(0, self.panel_video.mostrar, anotado)
            self._actualizar_analisis()

            dt_actual = time.time() - t_inicio
            if dt_actual < dt_target:
                time.sleep(dt_target - dt_actual)

        self.ejecutando = False
        n = len(self.t_list)
        if n > 0:
            self.after(0, lambda: self._set_estado(
                f"✓  Completado ({n} pts)", "#aed581"))
        else:
            self.after(0, lambda: self._set_estado(
                "⚠  Sin detección", "#ef9a9a"))

    # ─── ANÁLISIS ───
    def _actualizar_analisis(self):
        if len(self.t_list) < 3:
            return
        x = np.array(self.x_list, dtype=float)
        y = np.array(self.y_list, dtype=float)
        signal = x if np.var(x) >= np.var(y) else y
        self._actualizar_todo(signal)

    def _actualizar_todo(self, signal):
        t = np.array(self.t_list, dtype=float)
        if len(t) < 3:
            return

        v = kinematics.derivada_central(signal, t)
        a = kinematics.segunda_derivada(signal, t)
        v = kinematics.suavizar(v, window=5)
        a = kinematics.suavizar(a, window=5)

        # El usuario eligió tipo manual → lo respetamos
        tipo = self.tipo_movimiento.get()
        a_prom = float(np.nanmean(a)) if len(a) else 0.0
        v_prom = float(np.nanmean(v)) if len(v) else 0.0

        dist = kinematics.distancia_total(self.x_list, self.y_list)
        t_total = float(t[-1] - t[0])

        x_teo = None
        try:
            res = validator.validar(tipo, t, signal)
            err = res["error_medio"]
            x_teo = res["x_teo"]
        except Exception:
            err = float("nan")

        def _set_kpis():
            self.var_tipo.set(tipo)
            self.var_vprom.set(f"{v_prom:.3f}")
            self.var_aprom.set(f"{a_prom:.3f}")
            self.var_dist.set(f"{dist:.3f}")
            self.var_tiempo.set(f"{t_total:.3f}")
            self.var_error.set(f"{err:.2f}" if not np.isnan(err) else "—")

        self.after(0, _set_kpis)
        _t, _s, _v, _a, _xt = t, signal, v, a, x_teo
        self.after(0, lambda: self.panel_graf.actualizar(_t, _s, _v, _a, _xt))

        self._ultimo = {
            "t": t, "x": np.array(self.x_list, dtype=float),
            "y": np.array(self.y_list, dtype=float),
            "signal": signal, "v": v, "a": a, "tipo": tipo,
            "v_prom": v_prom, "a_prom": a_prom, "dist": dist,
            "t_total": t_total, "error": err,
        }

    # ─── SIMULACIÓN ───
    def _ejecutar_simulacion(self):
        tipo = self.tipo_movimiento.get()
        datos_input = {}
        for clave, var in self._sim_vars.items():
            calcular = self._sim_check[clave].get()
            valor = var.get().strip()
            if calcular or valor == "":
                datos_input[clave] = None
            else:
                try:
                    datos_input[clave] = float(valor)
                except ValueError:
                    messagebox.showerror("Simulación",
                        f"'{clave}' no es un número válido.")
                    return

        try:
            resuelto = resolver_por_tipo(tipo, datos_input)
        except ErrorSolver as exc:
            messagebox.showerror("Simulación · Solver",
                f"No se pudo resolver:\n{exc}\n\n"
                f"Asegurate de dejar UN solo campo vacío.")
            return
        except Exception as exc:
            messagebox.showerror("Simulación", f"Error: {exc}")
            return

        if resuelto.get("incognita"):
            inc = resuelto["incognita"]
            valor = resuelto[inc]
            self._lbl_sim_resultado.config(
                text=f"✓ Calculado:  {inc} = {valor:.4f}",
                fg=self.C_VERDE,
            )
            try:
                self._sim_vars[inc].set(f"{valor:.4f}")
                self._sim_check[inc].set(False)
            except KeyError:
                pass

        try:
            ruido = float(self.sim_ruido.get())
        except Exception:
            ruido = 0.0

        if tipo == "MRU":
            x0_, v0_, a_, t_t = (float(resuelto["x0"]), float(resuelto["v"]),
                                  0.0, float(resuelto["t"]))
        elif tipo == "MRUV":
            x0_, v0_, a_, t_t = (float(resuelto["x0"]), float(resuelto["v0"]),
                                  float(resuelto["a"]), float(resuelto["t"]))
        else:
            x0_, v0_, a_, t_t = (float(resuelto["y0"]), float(resuelto["v0"]),
                                  -9.8, float(resuelto["t"]))

        if t_t <= 0:
            messagebox.showerror("Simulación",
                "El tiempo total resultante es 0 o negativo.")
            return

        try:
            datos = simular(tipo=tipo, x0=x0_, v0=v0_, a=a_,
                           t_total=t_t, fps=30, ruido=ruido)
        except Exception as exc:
            messagebox.showerror("Simulación", f"Error: {exc}")
            return

        self.t_list = list(datos["t"])
        self.x_list = list(datos["x"])
        self.y_list = list(datos["y"])
        self._actualizar_todo(np.array(datos["signal"]))
        self._set_estado(f"✓  Simulación lista", "#81d4fa")

    # ─── EXPORTACIÓN ───
    def exportar_csv(self):
        if not self._ultimo:
            messagebox.showinfo("Exportar", "Aún no hay datos.")
            return
        ruta = filedialog.asksaveasfilename(defaultextension=".csv",
            filetypes=[("CSV", "*.csv")], title="Guardar CSV")
        if not ruta:
            return
        u = self._ultimo
        try:
            data_exporter.exportar_csv(ruta, u["t"], u["x"], u["y"],
                                        u["v"], u["a"], u["tipo"])
            messagebox.showinfo("Exportar", f"CSV guardado en:\n{ruta}")
        except Exception as exc:
            messagebox.showerror("Exportar", f"Error: {exc}")
