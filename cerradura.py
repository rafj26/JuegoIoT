from dispositivo_base import DispositivoBase


class Cerradura(DispositivoBase):
    def get_nombre_tipo(self):
        return "Cerradura Inteligente"

    def get_mensaje_alerta_real(self):
        return "Intento de apertura forzada"

    def get_mensaje_alerta_falsa(self):
        return "Actividad en cerradura"

    def calcular_probabilidad_real(self, hora_actual):
        probabilidad = super().calcular_probabilidad_real(hora_actual)

        # Noche aumenta probabilidad significativamente
        if hora_actual.hour >= 23 or hora_actual.hour <= 4:
            probabilidad += 0.3

        return max(0.1, min(0.9, probabilidad))