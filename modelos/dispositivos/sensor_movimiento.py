"""Sensor de movimiento."""
from modelos.dispositivos.dispositivo_base import DispositivoBase


class SensorMovimiento(DispositivoBase):
    """
    Sensor de movimiento.

    Los fines de semana suman 0.15 a la probabilidad de alerta real.
    """

    def get_nombre_tipo(self):
        """Devuelve el nombre legible del dispositivo."""
        return "Sensor de Movimiento"

    def get_mensaje_alerta_real(self):
        """Devuelve el mensaje mostrado en una alerta real."""
        return "Movimiento detectado en area restringida"

    def get_mensaje_alerta_falsa(self):
        """Devuelve el mensaje mostrado en una falsa alarma."""
        return "Movimiento detectado"

    def calcular_probabilidad_real(self, hora_actual):
        """
        Calcula la probabilidad de alerta real ajustada a este dispositivo.

        Args:
            hora_actual (datetime): Momento de la ronda.

        Returns:
            float: Probabilidad entre 0.1 y 0.9.
        """
        probabilidad = super().calcular_probabilidad_real(hora_actual)

        # Fines de semana aumentan probabilidad
        if hora_actual.weekday() >= 5:
            probabilidad += 0.15

        return max(0.1, min(0.9, probabilidad))
