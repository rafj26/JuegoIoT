import random
from sensor_movimiento import SensorMovimiento
from sensor_temperatura import SensorTemperatura
from sensor_energia import SensorEnergia
from sensor_rfid import SensorRFID
from sensor_ruido import SensorRuido
from camara import Camara
from router import Router
from cerradura import Cerradura


# Clase para gestionar la red de dispositivos
class RedIoT:
    def __init__(self):
        self.dispositivos = []
        self.ubicaciones = [
            "Entrada Principal",
            "Sala de Servidores",
            "Oficina 1",
            "Oficina 2",
            "Pasillo",
            "Estacionamiento",
            "Recepcion",
            "Almacen"
        ]
        self._inicializar_dispositivos()

    def _inicializar_dispositivos(self):
        # Lista de clases de dispositivos
        clases_dispositivos = [
            SensorMovimiento,
            SensorTemperatura,
            SensorEnergia,
            SensorRFID,
            SensorRuido,
            Camara,
            Router,
            Cerradura
        ]

        # Crea un dispositivo de cada tipo
        for i, clase in enumerate(clases_dispositivos):
            id_dispositivo = f"DEV-{i + 1:03d}"
            ubicacion = self.ubicaciones[i]
            dispositivo = clase(id_dispositivo, ubicacion)
            self.dispositivos.append(dispositivo)

    def generar_alertas_turno(self, hora_actual):
        # Genera alertas de todos los dispositivos
        return [dispositivo.generar_alerta(hora_actual)
                for dispositivo in self.dispositivos]