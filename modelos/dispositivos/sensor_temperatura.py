"""Sensor de temperatura."""
from modelos.dispositivos.dispositivo_base import DispositivoBase


class SensorTemperatura(DispositivoBase):
    """
    Sensor de temperatura.

    Entre las 12:00 y las 16:00 suma 0.1 a la probabilidad de alerta real.
    """

    def get_nombre_tipo(self):
        """Devuelve el nombre legible del dispositivo."""
        return "Sensor de Temperatura"

    def get_mensaje_alerta_real(self):
        """Devuelve el mensaje mostrado en una alerta real."""
        return "Temperatura critica detectada"

    def get_mensaje_alerta_falsa(self):
        """Devuelve el mensaje mostrado en una falsa alarma."""
        return "Fluctuacion de temperatura"

    def calcular_probabilidad_real(self, hora_actual):
        """
        Calcula la probabilidad de alerta real ajustada a este dispositivo.

        Args:
            hora_actual (datetime): Momento de la ronda.

        Returns:
            float: Probabilidad entre 0.1 y 0.9.
        """
        probabilidad = super().calcular_probabilidad_real(hora_actual)

        # Horas de calor aumentan probabilidad
        if 12 <= hora_actual.hour <= 16:
            probabilidad += 0.1

        return max(0.1, min(0.9, probabilidad))
