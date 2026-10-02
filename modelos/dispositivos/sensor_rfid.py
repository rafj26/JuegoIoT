"""Sensor de control de acceso RFID."""
from modelos.dispositivos.dispositivo_base import DispositivoBase


class SensorRFID(DispositivoBase):
    """
    Sensor de control de acceso RFID.

    Antes de las 7:00 o despues de las 19:00 suma 0.2 a la probabilidad de alerta real.
    """

    def get_nombre_tipo(self):
        """Devuelve el nombre legible del dispositivo."""
        return "Sensor RFID"

    def get_mensaje_alerta_real(self):
        """Devuelve el mensaje mostrado en una alerta real."""
        return "Acceso no autorizado detectado"

    def get_mensaje_alerta_falsa(self):
        """Devuelve el mensaje mostrado en una falsa alarma."""
        return "Tarjeta escaneada"

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
        if hora_actual.hour < 7 or hora_actual.hour > 19:
            probabilidad += 0.2

        return max(0.1, min(0.9, probabilidad))
