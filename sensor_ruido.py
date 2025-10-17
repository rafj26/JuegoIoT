from dispositivo_base import DispositivoBase


class SensorRuido(DispositivoBase):
    def get_nombre_tipo(self):
        return "Sensor de Ruido"

    def get_mensaje_alerta_real(self):
        return "Nivel de ruido inusual"

    def get_mensaje_alerta_falsa(self):
        return "Ruido ambiental detectado"

    def calcular_probabilidad_real(self, hora_actual):
        probabilidad = super().calcular_probabilidad_real(hora_actual)

        # Noche aumenta probabilidad
        if 22 <= hora_actual.hour or hora_actual.hour <= 5:
            probabilidad += 0.2

        return max(0.1, min(0.9, probabilidad))