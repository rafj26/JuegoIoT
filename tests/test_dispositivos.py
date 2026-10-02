from datetime import datetime

import pytest

from modelos.alerta import Alerta
from modelos.dispositivos import (Camara, Cerradura, DispositivoBase, Router, SensorEnergia,
                                  SensorMovimiento, SensorRFID, SensorRuido, SensorTemperatura)

LUNES = datetime(2025, 1, 6)
SABADO = datetime(2025, 1, 11)


def a_las(hora, dia=LUNES):
    return dia.replace(hour=hora)


DISPOSITIVOS = {
    SensorMovimiento: ("Sensor de Movimiento", "Movimiento detectado en area restringida",
                       "Movimiento detectado"),
    SensorTemperatura: ("Sensor de Temperatura", "Temperatura critica detectada",
                        "Fluctuacion de temperatura"),
    SensorEnergia: ("Sensor de Energia", "Consumo anomalo de energia", "Variacion en consumo"),
    SensorRFID: ("Sensor RFID", "Acceso no autorizado detectado", "Tarjeta escaneada"),
    SensorRuido: ("Sensor de Ruido", "Nivel de ruido inusual", "Ruido ambiental detectado"),
    Camara: ("Camara", "Movimiento sospechoso capturado", "Actividad registrada"),
    Router: ("Router", "Trafico de red sospechoso", "Pico de trafico detectado"),
    Cerradura: ("Cerradura Inteligente", "Intento de apertura forzada", "Actividad en cerradura"),
}


@pytest.mark.parametrize("clase", DISPOSITIVOS)
class TestCadaDispositivo:
    def test_es_dispositivo_base(self, clase):
        dispositivo = clase("DEV-X", "Lugar")
        assert isinstance(dispositivo, DispositivoBase)
        assert dispositivo.id == "DEV-X" and dispositivo.ubicacion == "Lugar"

    def test_mensajes(self, clase):
        nombre, real, falsa = DISPOSITIVOS[clase]
        dispositivo = clase("DEV-X", "Lugar")
        assert dispositivo.get_nombre_tipo() == nombre
        assert dispositivo.get_mensaje_alerta_real() == real
        assert dispositivo.get_mensaje_alerta_falsa() == falsa

    def test_genera_alerta_real(self, clase, monkeypatch):
        monkeypatch.setattr("modelos.dispositivos.dispositivo_base.random.random", lambda: 0.0)
        dispositivo = clase("DEV-X", "Lugar")
        alerta = dispositivo.generar_alerta(a_las(10))
        assert isinstance(alerta, Alerta)
        assert alerta.es_real
        assert alerta.mensaje == DISPOSITIVOS[clase][1]
        assert alerta.dispositivo is dispositivo
        assert alerta.hora == a_las(10)

    def test_genera_alerta_falsa(self, clase, monkeypatch):
        monkeypatch.setattr("modelos.dispositivos.dispositivo_base.random.random", lambda: 0.999)
        alerta = clase("DEV-X", "Lugar").generar_alerta(a_las(10))
        assert not alerta.es_real
        assert alerta.mensaje == DISPOSITIVOS[clase][2]

    def test_probabilidad_en_limites(self, clase):
        dispositivo = clase("DEV-X", "Lugar")
        for dia in (LUNES, SABADO):
            for hora in range(24):
                assert 0.1 <= dispositivo.calcular_probabilidad_real(a_las(hora, dia)) <= 0.9


@pytest.mark.parametrize("clase, momento, esperado", [
    # Base: 0.4, noche (>=22 o <=6) +0.2, horario laboral (9-17) -0.1
    (SensorMovimiento, a_las(10), 0.3),
    (SensorMovimiento, a_las(10, SABADO), 0.45),
    (SensorMovimiento, a_las(2), 0.6),
    (SensorMovimiento, a_las(2, SABADO), 0.75),
    (SensorTemperatura, a_las(10), 0.3),
    (SensorTemperatura, a_las(14), 0.4),
    (SensorTemperatura, a_las(8), 0.4),
    (SensorEnergia, a_las(20), 0.4),
    (SensorEnergia, a_las(21), 0.55),
    (SensorEnergia, a_las(22), 0.75),
    (SensorRFID, a_las(10), 0.3),
    (SensorRFID, a_las(20), 0.6),
    (SensorRFID, a_las(2), 0.8),
    (SensorRuido, a_las(20), 0.4),
    (SensorRuido, a_las(23), 0.8),
    (Camara, a_las(6), 0.6),
    (Camara, a_las(3), 0.85),
    (Router, a_las(0), 0.6),
    (Router, a_las(3), 0.85),
    (Cerradura, a_las(6), 0.6),
    (Cerradura, a_las(23), 0.9),
    (Cerradura, a_las(3), 0.9),
])
def test_probabilidades_por_contexto(clase, momento, esperado):
    assert clase("DEV-X", "Lugar").calcular_probabilidad_real(momento) == pytest.approx(esperado)


def test_probabilidad_base_sin_ajustes_propios():
    class SensorExtremo(DispositivoBase):
        def get_nombre_tipo(self):
            return "Extremo"

        def get_mensaje_alerta_real(self):
            return "real"

        def get_mensaje_alerta_falsa(self):
            return "falsa"

    sensor = SensorExtremo("X", "Y")
    assert sensor.calcular_probabilidad_real(a_las(2)) == pytest.approx(0.6)


def test_clase_base_es_abstracta():
    with pytest.raises(TypeError):
        DispositivoBase("X", "Y")


def test_frecuencia_de_alertas_reales_sigue_probabilidad():
    import random
    random.seed(1234)
    sensor = Cerradura("DEV-008", "Almacen")
    reales = sum(sensor.generar_alerta(a_las(23)).es_real for _ in range(2000))
    assert 0.86 < reales / 2000 < 0.94


def test_info_formateada_de_alerta():
    sensor = Router("DEV-007", "Recepcion")
    alerta = Alerta(sensor, "Trafico de red sospechoso", True, a_las(14))
    assert alerta.get_info_formateada(3) == {
        'indice': 3, 'hora': "14:00", 'tipo': "Router", 'ubicacion': "Recepcion",
        'mensaje': "Trafico de red sospechoso", 'id': "DEV-007",
    }
    assert alerta.atendida is False
