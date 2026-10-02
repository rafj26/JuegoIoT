"""Sensor de consumo energetico."""
from modelos.dispositivos.dispositivo_base import DispositivoBase


class SensorEnergia(DispositivoBase):
    """
    Sensor de consumo energetico.

    Antes de las 6:00 o despues de las 20:00 suma 0.15 a la probabilidad de alerta real.
    """

    def get_nombre_tipo(self):
        """Devuelve el nombre legible del dispositivo."""
        return "Sensor de Energia"

    def get_mensaje_alerta_real(self):
        """Devuelve el mensaje mostrado en una alerta real."""
        return "Consumo anomalo de energia"

    def get_mensaje_alerta_falsa(self):
        """Devuelve el mensaje mostrado en una falsa alarma."""
        return "Variacion en consumo"

    def calcular_probabilidad_real(self, hora_actual):
        """
        Calcula la probabilidad de alerta real ajustada a este dispositivo.

        Args:
            hora_actual (datetime): Momento de la ronda.

        Returns:
            float: Probabilidad entre 0.1 y 0.9.
        """
        probabilidad = super().calcular_probabilidad_real(hora_actual)

        # Fuera de horario laboral aumenta probabilidad
        if hora_actual.hour < 6 or hora_actual.hour > 20:
            probabilidad += 0.15

        return max(0.1, min(0.9, probabilidad))
