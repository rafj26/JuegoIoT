from modelos.dispositivos.dispositivo_base import DispositivoBase


class SensorMovimiento(DispositivoBase):
    def get_nombre_tipo(self):
        return "Sensor de Movimiento"

    def get_mensaje_alerta_real(self):
        return "Movimiento detectado en area restringida"

    def get_mensaje_alerta_falsa(self):
        return "Movimiento detectado"

    def calcular_probabilidad_real(self, hora_actual):
        # Personaliza probabilidad para este sensor
        probabilidad = super().calcular_probabilidad_real(hora_actual)

        # Fines de semana aumentan probabilidad
        if hora_actual.weekday() >= 5:
            probabilidad += 0.15

        return max(0.1, min(0.9, probabilidad))