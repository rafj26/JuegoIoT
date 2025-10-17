from dispositivo_base import DispositivoBase


class SensorEnergia(DispositivoBase):
    def get_nombre_tipo(self):
        return "Sensor de Energia"

    def get_mensaje_alerta_real(self):
        return "Consumo anomalo de energia"

    def get_mensaje_alerta_falsa(self):
        return "Variacion en consumo"

    def calcular_probabilidad_real(self, hora_actual):
        probabilidad = super().calcular_probabilidad_real(hora_actual)

        # Fuera de horario laboral aumenta probabilidad
        if hora_actual.hour < 6 or hora_actual.hour > 20:
            probabilidad += 0.15

        return max(0.1, min(0.9, probabilidad))