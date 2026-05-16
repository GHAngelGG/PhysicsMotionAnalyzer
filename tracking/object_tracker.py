"""
Rastreador de objetos por color con modo "fijador" (lock-on).

Selecciona el blob de color HSV correcto usando dos estrategias:
  1) Si tenemos una posición previa (o un objetivo fijado por clic):
     elegimos el blob cuyo centro esté MÁS CERCA de esa posición.
  2) Si es la primera detección y no hay objetivo: el blob más grande.

Esto evita que el sistema se "distraiga" con otros objetos del mismo color
(p. ej. un cojín rosado al fondo si la pelota es roja).
"""
import math

import cv2

from tracking.color_detector import generar_mascara


class RastreadorObjeto:
    """
    Rastrea un objeto de color a lo largo de una secuencia de frames.

    Atributos:
        max_trayectoria (int): número máximo de puntos guardados.
        trayectoria (list[tuple[int,int]]): últimas posiciones (x, y) en píxeles.
        objetivo_inicial (tuple|None): (x, y) donde el usuario clicó en el calibrador.
        radio_referencia (int): radio aproximado del objeto, usado para filtrar tamaños.
        distancia_max (int): distancia máxima en píxeles entre detecciones consecutivas.
        ultima_posicion (tuple|None): última posición conocida del objeto.
    """

    def __init__(self, max_trayectoria=256):
        self.max_trayectoria = max_trayectoria
        self.trayectoria = []
        # Modo fijador
        self.objetivo_inicial = None       # (x, y) del clic en calibrador
        self.radio_referencia = 0          # radio aprox. del objeto fijado
        self.distancia_max = 200           # px: salto máximo entre frames
        self.ultima_posicion = None        # se actualiza en cada detección

    # ──────────────────────────────────────── API
    def fijar_objetivo(self, x, y, radio_referencia=0, distancia_max=None):
        """
        Fija el objetivo a seguir (típicamente desde el clic del calibrador).

        Parámetros:
            x, y (int): coordenadas en píxeles del frame original.
            radio_referencia (int): radio aproximado del objeto (px).
            distancia_max (int|None): salto máximo permitido entre frames.
                Si es None y hay radio_referencia, se calcula automáticamente
                como 8 × radio_referencia.
        """
        self.objetivo_inicial = (int(x), int(y))
        self.ultima_posicion = (int(x), int(y))
        self.radio_referencia = int(radio_referencia)
        if distancia_max is None and radio_referencia > 0:
            self.distancia_max = max(80, 8 * radio_referencia)
        elif distancia_max is not None:
            self.distancia_max = int(distancia_max)

    def reiniciar(self, mantener_objetivo=False):
        """
        Limpia la trayectoria. Por defecto también olvida el objetivo fijado.

        Parámetros:
            mantener_objetivo (bool): si True, conserva el lock-on configurado.
        """
        self.trayectoria.clear()
        if not mantener_objetivo:
            self.objetivo_inicial = None
            self.radio_referencia = 0
            self.ultima_posicion = None
        else:
            # Reseteamos solo la última posición al objetivo inicial
            self.ultima_posicion = self.objetivo_inicial

    # ──────────────────────────────────────── DETECCIÓN
    def procesar(self, frame_bgr, hsv_min, hsv_max, area_minima=80):
        """
        Procesa un frame y detecta el objeto por color.

        Si hay un objetivo fijado o una posición previa, elige el blob
        más cercano. Si no, elige el más grande (modo legacy).

        Retorna:
            (centro, radio, mask, frame_anotado)
        """
        mask = generar_mascara(frame_bgr, hsv_min, hsv_max)
        contornos, _ = cv2.findContours(
            mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        anotado = frame_bgr.copy()
        centro = None
        radio = 0

        # Filtrar contornos por área mínima (evita ruido)
        candidatos = [c for c in contornos if cv2.contourArea(c) >= area_minima]

        # Filtro adicional por área máxima si conocemos el radio del objetivo
        if self.radio_referencia > 0:
            area_ref = math.pi * (self.radio_referencia ** 2)
            area_max = area_ref * 9.0   # hasta 3x el radio en área
            candidatos = [c for c in candidatos if cv2.contourArea(c) <= area_max]

        if candidatos:
            elegido = self._elegir_contorno(candidatos)
            ((_x, _y), r) = cv2.minEnclosingCircle(elegido)
            momentos = cv2.moments(elegido)
            if momentos["m00"] > 0:
                cx = int(momentos["m10"] / momentos["m00"])
                cy = int(momentos["m01"] / momentos["m00"])
                centro = (cx, cy)
                radio = int(r)

                # Validar salto máximo si tenemos posición previa
                if self.ultima_posicion is not None:
                    dx = cx - self.ultima_posicion[0]
                    dy = cy - self.ultima_posicion[1]
                    dist = math.hypot(dx, dy)
                    if dist > self.distancia_max:
                        # Salto demasiado grande: probablemente es otro objeto
                        # del mismo color. Mantenemos la posición anterior y
                        # NO actualizamos la trayectoria.
                        centro = None
                        radio = 0

                if centro is not None:
                    self.ultima_posicion = centro
                    self.trayectoria.append(centro)
                    if len(self.trayectoria) > self.max_trayectoria:
                        self.trayectoria.pop(0)

                    # Dibujar el objeto detectado
                    cv2.circle(anotado, centro, radio, (0, 255, 255), 2)
                    cv2.circle(anotado, centro, 4, (0, 0, 255), -1)
                    cv2.putText(
                        anotado,
                        f"({cx}, {cy})",
                        (cx + 10, cy - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (255, 255, 255),
                        1,
                    )

        # Dibujar la trayectoria con efecto cola
        for i in range(1, len(self.trayectoria)):
            p1 = self.trayectoria[i - 1]
            p2 = self.trayectoria[i]
            grosor = max(1, int(2 + (i / self.max_trayectoria) * 3))
            cv2.line(anotado, p1, p2, (0, 255, 0), grosor)

        # Si hay objetivo fijado y aún no se detectó nada, dibujar el target
        if centro is None and self.ultima_posicion is not None:
            cv2.circle(anotado, self.ultima_posicion, 12, (255, 0, 255), 2)
            cv2.line(anotado,
                     (self.ultima_posicion[0] - 18, self.ultima_posicion[1]),
                     (self.ultima_posicion[0] + 18, self.ultima_posicion[1]),
                     (255, 0, 255), 1)
            cv2.line(anotado,
                     (self.ultima_posicion[0], self.ultima_posicion[1] - 18),
                     (self.ultima_posicion[0], self.ultima_posicion[1] + 18),
                     (255, 0, 255), 1)

        return centro, radio, mask, anotado

    # ──────────────────────────────────────── ESTRATEGIA DE SELECCIÓN
    def _elegir_contorno(self, candidatos):
        """
        Elige el contorno apropiado según el modo:
          - Si hay posición previa: el contorno cuyo centro esté MÁS CERCA.
          - Si no: el contorno de mayor área.
        """
        if self.ultima_posicion is None:
            return max(candidatos, key=cv2.contourArea)

        # Modo "fijador": elegir por proximidad a la última posición
        ux, uy = self.ultima_posicion

        def distancia_centro(contorno):
            momentos = cv2.moments(contorno)
            if momentos["m00"] <= 0:
                return float("inf")
            cx = momentos["m10"] / momentos["m00"]
            cy = momentos["m01"] / momentos["m00"]
            return math.hypot(cx - ux, cy - uy)

        return min(candidatos, key=distancia_centro)
