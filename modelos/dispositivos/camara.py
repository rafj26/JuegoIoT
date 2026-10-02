"""Camara de vigilancia."""
from modelos.dispositivos.dispositivo_base import DispositivoBase


class Camara(DispositivoBase):
    """
    Camara de vigilancia.

    Entre las 0:00 y las 5:00 suma 0.25 a la probabilidad de alerta real.
    """

    def get_nombre_tipo(self):
        """Devuelve el nombre legible del dispositivo."""
        return "Camara"

    def get_mensaje_alerta_real(self):
        """Devuelve el mensaje mostrado en una alerta real."""
        return "Movimiento sospechoso capturado"

    def get_mensaje_alerta_falsa(self):
        """Devuelve el mensaje mostrado en una falsa alarma."""
        return "Actividad registrada"

    def calcular_probabilidad_real(self, hora_actual):
        """
        Calcula la probabilidad de alerta real ajustada a este dispositivo.

        Args:
            hora_actual (datetime): Momento de la ronda.

        Returns:
            float: Probabilidad entre 0.1 y 0.9.
        """
        probabilidad = super().calcular_probabilidad_real(hora_actual)

        # Madrugada aumenta probabilidad
        if 0 <= hora_actual.hour <= 5:
            probabilidad += 0.25

        return max(0.1, min(0.9, probabilidad))
