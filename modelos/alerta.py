# Clase para representar una alerta
class Alerta:
    def __init__(self, dispositivo, mensaje, es_real, hora):
        self.dispositivo = dispositivo
        self.mensaje = mensaje
        self.es_real = es_real
        self.hora = hora
        self.atendida = False

    def get_info_formateada(self, indice):
        # Retorna informacion formateada como diccionario
        return {
            'indice': indice,
            'hora': self.hora.strftime("%H:%M"),
            'tipo': self.dispositivo.get_nombre_tipo(),
            'ubicacion': self.dispositivo.ubicacion,
            'mensaje': self.mensaje,
            'id': self.dispositivo.id
        }