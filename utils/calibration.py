"""
Calibración espacial: conversión píxeles <-> metros.

El usuario indica cuántos píxeles corresponden a un metro real mediante
una referencia conocida en el video (por ejemplo una regla).
"""


class Calibracion:
    """
    Conversor de unidades píxel-metro.

    Atributos:
        ppm (float): píxeles por metro (siempre > 0).
    """

    def __init__(self, pixeles_por_metro=100.0):
        """
        Parámetros:
            pixeles_por_metro (float): factor de escala inicial.
        """
        self.ppm = self._validar(pixeles_por_metro)

    @staticmethod
    def _validar(valor):
        """Asegura que el factor sea positivo y no nulo."""
        try:
            v = float(valor)
        except (TypeError, ValueError):
            v = 1.0
        if v <= 0:
            v = 1e-6
        return v

    def set_ppm(self, valor):
        """Actualiza el factor de escala (píxeles por metro)."""
        self.ppm = self._validar(valor)

    def pix_a_m(self, valor_pix):
        """
        Convierte un valor (o array) de píxeles a metros.

        Parámetros:
            valor_pix (float | np.ndarray): valor en píxeles.

        Retorna:
            float | np.ndarray: valor en metros.
        """
        return valor_pix / self.ppm

    def m_a_pix(self, valor_m):
        """
        Convierte un valor (o array) de metros a píxeles.

        Parámetros:
            valor_m (float | np.ndarray): valor en metros.

        Retorna:
            float | np.ndarray: valor en píxeles.
        """
        return valor_m * self.ppm
