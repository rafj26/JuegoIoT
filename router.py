from dispositivo_base import DispositivoBase


class Router(DispositivoBase):
    def get_nombre_tipo(self):
        return "Router"

    def get_mensaje_alerta_real(self):
        return "Trafico de red sospechoso"

    def get_mensaje_alerta_falsa(self):
        return "Pico de trafico detectado"

    def calcular_probabilidad_real(self, hora_actual):
        probabilidad = super().calcular_probabilidad_real(hora_actual)

        # Madrugada aumenta probabilidad de ataques
        if 1 <= hora_actual.hour <= 5:
            probabilidad += 0.25

        return max(0.1, min(0.9, probabilidad))