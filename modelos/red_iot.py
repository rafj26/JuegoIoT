from modelos.dispositivos.sensor_movimiento import SensorMovimiento
from modelos.dispositivos.sensor_temperatura import SensorTemperatura
from modelos.dispositivos.sensor_energia import SensorEnergia
from modelos.dispositivos.sensor_rfid import SensorRFID
from modelos.dispositivos.sensor_ruido import SensorRuido
from modelos.dispositivos.camara import Camara
from modelos.dispositivos.router import Router
from modelos.dispositivos.cerradura import Cerradura


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