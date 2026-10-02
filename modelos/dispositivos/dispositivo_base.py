import random
from abc import ABC, abstractmethod

from modelos.alerta import Alerta


# Clase abstracta base para todos los dispositivos
class DispositivoBase(ABC):
    def __init__(self, id_dispositivo, ubicacion):
        self.id = id_dispositivo
        self.ubicacion = ubicacion

    @abstractmethod
    def get_nombre_tipo(self):
        # Retorna el nombre del tipo de dispositivo
        pass

    @abstractmethod
    def get_mensaje_alerta_real(self):
        # Retorna mensaje para alerta real
        pass

    @abstractmethod
    def get_mensaje_alerta_falsa(self):
        # Retorna mensaje para alerta falsa
        pass

    def calcular_probabilidad_real(self, hora_actual):
        # Calcula probabilidad base de alerta real
        probabilidad = 0.4

        # Horario nocturno aumenta probabilidad
        if hora_actual.hour >= 22 or hora_actual.hour <= 6:
            probabilidad += 0.2

        # Horario laboral disminuye probabilidad
        if 9 <= hora_actual.hour <= 17:
            probabilidad -= 0.1

        return max(0.1, min(0.9, probabilidad))

    def generar_alerta(self, hora_actual):
        # Genera alerta del dispositivo
        probabilidad = self.calcular_probabilidad_real(hora_actual)
        es_real = random.random() < probabilidad

        if es_real:
            mensaje = self.get_mensaje_alerta_real()
        else:
            mensaje = self.get_mensaje_alerta_falsa()

        return Alerta(self, mensaje, es_real, hora_actual)