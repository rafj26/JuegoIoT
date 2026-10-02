from modelos.dispositivos.dispositivo_base import DispositivoBase


class Camara(DispositivoBase):
    def get_nombre_tipo(self):
        return "Camara"

    def get_mensaje_alerta_real(self):
        return "Movimiento sospechoso capturado"

    def get_mensaje_alerta_falsa(self):
        return "Actividad registrada"

    def calcular_probabilidad_real(self, hora_actual):
        probabilidad = super().calcular_probabilidad_real(hora_actual)

        # Madrugada aumenta probabilidad
        if 0 <= hora_actual.hour <= 5:
            probabilidad += 0.25

        return max(0.1, min(0.9, probabilidad))