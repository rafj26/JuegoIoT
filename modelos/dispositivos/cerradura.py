"""Cerradura inteligente."""
from modelos.dispositivos.dispositivo_base import DispositivoBase


class Cerradura(DispositivoBase):
    """
    Cerradura inteligente.

    Entre las 23:00 y las 4:00 suma 0.3 a la probabilidad de alerta real.
    """

    def get_nombre_tipo(self):
        """Devuelve el nombre legible del dispositivo."""
        return "Cerradura Inteligente"

    def get_mensaje_alerta_real(self):
        """Devuelve el mensaje mostrado en una alerta real."""
        return "Intento de apertura forzada"

    def get_mensaje_alerta_falsa(self):
        """Devuelve el mensaje mostrado en una falsa alarma."""
        return "Actividad en cerradura"

    def calcular_probabilidad_real(self, hora_actual):
        """
        Calcula la probabilidad de alerta real ajustada a este dispositivo.

        Args:
            hora_actual (datetime): Momento de la ronda.

        Returns:
            float: Probabilidad entre 0.1 y 0.9.
        """
        probabilidad = super().calcular_probabilidad_real(hora_actual)

        # Noche aumenta probabilidad significativamente
        if hora_actual.hour >= 23 or hora_actual.hour <= 4:
            probabilidad += 0.3

        return max(0.1, min(0.9, probabilidad))