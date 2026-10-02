from modelos.dispositivos.dispositivo_base import DispositivoBase


class SensorTemperatura(DispositivoBase):
    def get_nombre_tipo(self):
        return "Sensor de Temperatura"

    def get_mensaje_alerta_real(self):
        return "Temperatura critica detectada"

    def get_mensaje_alerta_falsa(self):
        return "Fluctuacion de temperatura"

    def calcular_probabilidad_real(self, hora_actual):
        probabilidad = super().calcular_probabilidad_real(hora_actual)

        # Horas de calor aumentan probabilidad
        if 12 <= hora_actual.hour <= 16:
            probabilidad += 0.1

        return max(0.1, min(0.9, probabilidad))