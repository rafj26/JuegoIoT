"""Clase abstracta comun a todos los dispositivos IoT."""
import random
from abc import ABC, abstractmethod

from modelos.alerta import Alerta


class DispositivoBase(ABC):
    """
    Clase abstracta base para todos los dispositivos.

    Cada dispositivo concreto define su nombre, sus mensajes de alerta y,
    opcionalmente, ajusta la probabilidad de que una alerta sea real.

    Args:
        id_dispositivo (str): Identificador unico, por ejemplo ``"DEV-001"``.
        ubicacion (str): Lugar donde esta instalado.

    Attributes:
        id (str): Identificador unico del dispositivo.
        ubicacion (str): Lugar donde esta instalado.
    """

    def __init__(self, id_dispositivo, ubicacion):
        """Guarda el identificador y la ubicacion."""
        self.id = id_dispositivo
        self.ubicacion = ubicacion

    @abstractmethod
    def get_nombre_tipo(self):
        """
        Retorna el nombre del tipo de dispositivo.

        Returns:
            str: Nombre legible, por ejemplo ``"Sensor RFID"``.
        """
        pass

    @abstractmethod
    def get_mensaje_alerta_real(self):
        """
        Retorna mensaje para alerta real.

        Returns:
            str: Texto que describe una amenaza real.
        """
        pass

    @abstractmethod
    def get_mensaje_alerta_falsa(self):
        """
        Retorna mensaje para alerta falsa.

        Returns:
            str: Texto que describe una falsa alarma.
        """
        pass

    def calcular_probabilidad_real(self, hora_actual):
        """
        Calcula probabilidad base de alerta real.

        Parte de 0.4, suma 0.2 de noche (22:00-6:00) y resta 0.1 en horario
        laboral (9:00-17:00). Las subclases pueden ampliar esta regla.

        Args:
            hora_actual (datetime): Momento de la ronda.

        Returns:
            float: Probabilidad entre 0.1 y 0.9.
        """
        probabilidad = 0.4

        # Horario nocturno aumenta probabilidad
        if hora_actual.hour >= 22 or hora_actual.hour <= 6:
            probabilidad += 0.2

        # Horario laboral disminuye probabilidad
        if 9 <= hora_actual.hour <= 17:
            probabilidad -= 0.1

        return max(0.1, min(0.9, probabilidad))

    def generar_alerta(self, hora_actual):
        """
        Genera alerta del dispositivo.

        Args:
            hora_actual (datetime): Momento de la ronda.

        Returns:
            Alerta: Alerta real o falsa segun la probabilidad calculada.
        """
        probabilidad = self.calcular_probabilidad_real(hora_actual)
        es_real = random.random() < probabilidad

        if es_real:
            mensaje = self.get_mensaje_alerta_real()
        else:
            mensaje = self.get_mensaje_alerta_falsa()

        return Alerta(self, mensaje, es_real, hora_actual)
