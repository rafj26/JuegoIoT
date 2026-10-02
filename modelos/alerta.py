"""Alerta generada por un dispositivo IoT."""


class Alerta:
    """
    Clase para representar una alerta.

    Args:
        dispositivo (DispositivoBase): Dispositivo que genero la alerta.
        mensaje (str): Descripcion mostrada al jugador.
        es_real (bool): Si la alerta corresponde a una amenaza real.
        hora (datetime): Momento en que se genero.
    """

    def __init__(self, dispositivo, mensaje, es_real, hora):
        """Guarda los datos de la alerta."""
        self.dispositivo = dispositivo
        self.mensaje = mensaje
        self.es_real = es_real
        self.hora = hora
        self.atendida = False

    def get_info_formateada(self, indice):
        """
        Retorna informacion formateada como diccionario.

        Args:
            indice (int): Posicion de la alerta en la ronda (desde 1).

        Returns:
            dict: Claves ``indice``, ``hora``, ``tipo``, ``ubicacion``,
            ``mensaje`` e ``id``. No incluye si la alerta es real.
        """
        return {
            'indice': indice,
            'hora': self.hora.strftime("%H:%M"),
            'tipo': self.dispositivo.get_nombre_tipo(),
            'ubicacion': self.dispositivo.ubicacion,
            'mensaje': self.mensaje,
            'id': self.dispositivo.id
        }