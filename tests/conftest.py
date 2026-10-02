from datetime import datetime

import pytest

from modelos.alerta import Alerta
from modelos.dispositivos import SensorMovimiento
from modelos.juego import JuegoSeguridadIoT


@pytest.fixture
def juego():
    return JuegoSeguridadIoT()


@pytest.fixture
def dispositivo():
    return SensorMovimiento("DEV-001", "Entrada Principal")


@pytest.fixture
def crear_alerta(dispositivo):
    # Fabrica de alertas con valor real/falso controlado
    def _crear(es_real, hora=datetime(2025, 1, 6, 8, 0)):
        mensaje = (dispositivo.get_mensaje_alerta_real() if es_real
                   else dispositivo.get_mensaje_alerta_falsa())
        return Alerta(dispositivo, mensaje, es_real, hora)
    return _crear


@pytest.fixture
def juego_controlado(juego, crear_alerta):
    # Juego cuyas rondas tienen alertas fijas: [real, falsa, real, falsa]
    patron = [True, False, True, False]

    def generar(hora):
        return [crear_alerta(es_real, hora) for es_real in patron]

    juego.red.generar_alertas_turno = generar
    return juego
