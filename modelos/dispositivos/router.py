"""Router de red."""
from modelos.dispositivos.dispositivo_base import DispositivoBase


class Router(DispositivoBase):
    """
    Router de red.

    Entre la 1:00 y las 5:00 suma 0.25 a la probabilidad de alerta real.
    """

    def get_nombre_tipo(self):
        """Devuelve el nombre legible del dispositivo."""
        return "Router"

    def get_mensaje_alerta_real(self):
        """Devuelve el mensaje mostrado en una alerta real."""
        return "Trafico de red sospechoso"

    def get_mensaje_alerta_falsa(self):
        """Devuelve el mensaje mostrado en una falsa alarma."""
        return "Pico de trafico detectado"

    def calcular_probabilidad_real(self, hora_actual):
        """
        Calcula la probabilidad de alerta real ajustada a este dispositivo.

        Args:
            hora_actual (datetime): Momento de la ronda.

        Returns:
            float: Probabilidad entre 0.1 y 0.9.
        """
        probabilidad = super().calcular_probabilidad_real(hora_actual)

        # Madrugada aumenta probabilidad de ataques
        if 1 <= hora_actual.hour <= 5:
            probabilidad += 0.25

        return max(0.1, min(0.9, probabilidad))