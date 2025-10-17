from dispositivo_base import DispositivoBase


class SensorRFID(DispositivoBase):
    def get_nombre_tipo(self):
        return "Sensor RFID"

    def get_mensaje_alerta_real(self):
        return "Acceso no autorizado detectado"

    def get_mensaje_alerta_falsa(self):
        return "Tarjeta escaneada"

    def calcular_probabilidad_real(self, hora_actual):
        probabilidad = super().calcular_probabilidad_real(hora_actual)

        # Fuera de horario laboral aumenta probabilidad
        if hora_actual.hour < 7 or hora_actual.hour > 19:
            probabilidad += 0.2

        return max(0.1, min(0.9, probabilidad))