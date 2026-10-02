from datetime import datetime

from modelos.alerta import Alerta
from modelos.dispositivos import DispositivoBase
from modelos.red_iot import RedIoT


def test_genera_exactamente_8_dispositivos():
    red = RedIoT()
    assert len(red.dispositivos) == 8
    assert all(isinstance(d, DispositivoBase) for d in red.dispositivos)


def test_un_dispositivo_de_cada_tipo():
    tipos = {type(d).__name__ for d in RedIoT().dispositivos}
    assert tipos == {"SensorMovimiento", "SensorTemperatura", "SensorEnergia", "SensorRFID",
                     "SensorRuido", "Camara", "Router", "Cerradura"}


def test_ids_y_ubicaciones_unicos():
    red = RedIoT()
    assert [d.id for d in red.dispositivos] == [f"DEV-{i:03d}" for i in range(1, 9)]
    assert len({d.ubicacion for d in red.dispositivos}) == 8


def test_genera_una_alerta_por_dispositivo_en_cada_ronda():
    red = RedIoT()
    for hora in range(8, 21, 3):
        momento = datetime(2025, 1, 6, hora, 0)
        alertas = red.generar_alertas_turno(momento)
        assert len(alertas) == 8
        assert all(isinstance(a, Alerta) for a in alertas)
        assert [a.dispositivo for a in alertas] == red.dispositivos
        assert all(a.hora == momento for a in alertas)
