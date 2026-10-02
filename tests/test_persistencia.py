import csv
from datetime import datetime

import pytest

from modelos.persistencia import RepositorioPartidas


@pytest.fixture
def repo():
    with RepositorioPartidas(":memory:") as repositorio:
        yield repositorio


def partida_jugada(juego, seleccion=(1,)):
    while juego.tiene_rondas_pendientes():
        juego.iniciar_ronda()
        juego.procesar_decisiones(list(seleccion))
        juego.avanzar_ronda()
    return juego


def test_guardar_y_ver_historial(repo, juego_controlado):
    partida_jugada(juego_controlado)
    partida_id = repo.guardar_partida(juego_controlado, "Ana", fecha=datetime(2025, 1, 1, 10))
    historial = repo.ver_historial()
    assert historial == [{
        'id': partida_id, 'jugador': "Ana", 'fecha': "2025-01-01T10:00:00",
        'puntos_finales': juego_controlado.puntos, 'victoria': juego_controlado.puntos >= 15,
    }]


def test_rondas_guardadas(repo, juego_controlado):
    partida_jugada(juego_controlado)
    partida_id = repo.guardar_partida(juego_controlado, "Ana")
    rondas = repo.ver_rondas(partida_id)
    assert [r['numero'] for r in rondas] == [1, 2, 3, 4, 5]
    assert rondas[0]['alertas'][0]['es_real'] is True
    assert rondas[-1]['puntos_acumulados'] == juego_controlado.puntos


def test_historial_filtrado_y_ordenado(repo, juego):
    repo.guardar_partida(juego, "Ana", fecha=datetime(2025, 1, 1))
    repo.guardar_partida(juego, "Luis", fecha=datetime(2025, 1, 3))
    repo.guardar_partida(juego, "Ana", fecha=datetime(2025, 1, 2))
    assert [p['jugador'] for p in repo.ver_historial()] == ["Luis", "Ana", "Ana"]
    assert len(repo.ver_historial(jugador="Ana")) == 2
    assert len(repo.ver_historial(limite=1)) == 1


def test_estadisticas(repo, juego):
    juego.puntos = 20
    repo.guardar_partida(juego, "Ana")
    juego.puntos = 10
    repo.guardar_partida(juego, "Ana")
    juego.puntos = 5
    repo.guardar_partida(juego, "Luis")

    ana, luis = repo.ver_estadisticas()
    assert ana == {'jugador': "Ana", 'total_partidas': 2, 'victorias': 1, 'derrotas': 1,
                   'porcentaje_victorias': 50.0, 'mejor_puntuacion': 20, 'promedio_puntos': 15.0}
    assert luis['victorias'] == 0 and luis['mejor_puntuacion'] == 5
    assert repo.ver_estadisticas(jugador="Luis") == [luis]


def test_exportar_csv(repo, juego, tmp_path):
    repo.guardar_partida(juego, "Ana")
    repo.guardar_partida(juego, "Luis")
    ruta = tmp_path / "salida" / "historial.csv"
    assert repo.exportar_csv(str(ruta)) == 2
    with open(ruta, encoding="utf-8") as archivo:
        filas = list(csv.DictReader(archivo))
    assert {f['jugador'] for f in filas} == {"Ana", "Luis"}
    assert set(filas[0]) == {'id', 'jugador', 'fecha', 'puntos_finales', 'victoria'}


def test_base_en_archivo_persiste(tmp_path, juego):
    ruta = str(tmp_path / "datos" / "partidas.db")
    with RepositorioPartidas(ruta) as repo:
        repo.guardar_partida(juego, "Ana")
    with RepositorioPartidas(ruta) as repo:
        assert len(repo.ver_historial()) == 1
