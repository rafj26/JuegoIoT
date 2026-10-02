import builtins

import pytest

from controladores.controlador import Controlador
from modelos.juego import JuegoSeguridadIoT
from modelos.persistencia import RepositorioPartidas


def jugar_partida(juego, elegir):
    # Juega todas las rondas usando la funcion elegir(alertas) -> seleccion
    while juego.tiene_rondas_pendientes():
        juego.iniciar_ronda()
        juego.procesar_decisiones(elegir(juego.alertas_actuales))
        juego.avanzar_ronda()
    return juego.get_resultado_final()


def test_partida_completa_de_5_rondas_jugador_perfecto():
    juego = JuegoSeguridadIoT()
    resultado = jugar_partida(juego, lambda alertas: [i for i, a in enumerate(alertas, 1) if a.es_real])
    assert juego.ronda_actual == JuegoSeguridadIoT.TOTAL_RONDAS + 1
    assert len(juego.historial_rondas) == 5
    reales = sum(1 for r in juego.historial_rondas for a in r['alertas'] if a['es_real'])
    assert resultado['puntos_finales'] == 15 + 2 * reales
    assert resultado['victoria'] is True


def test_partida_completa_ignorando_todo():
    juego = JuegoSeguridadIoT()
    resultado = jugar_partida(juego, lambda alertas: [])
    reales = sum(1 for r in juego.historial_rondas for a in r['alertas'] if a['es_real'])
    assert resultado['puntos_finales'] == 15 - 2 * reales
    assert resultado['victoria'] is (reales == 0)


def test_victoria_y_derrota_controladas(juego_controlado):
    # Cada ronda: 2 reales y 2 falsas
    resultado = jugar_partida(juego_controlado, lambda alertas: [1, 2, 3, 4])
    assert resultado['puntos_finales'] == 15 + 5 * 2
    assert resultado['victoria']


def test_derrota_controlada(crear_alerta):
    juego = JuegoSeguridadIoT()
    juego.red.generar_alertas_turno = lambda hora: [crear_alerta(True, hora)]
    resultado = jugar_partida(juego, lambda alertas: [])
    assert resultado['puntos_finales'] == 15 - 5 * 2
    assert not resultado['victoria']


def test_historial_acumulado_coincide_con_puntos(juego_controlado):
    jugar_partida(juego_controlado, lambda alertas: [1])
    acumulado = 15
    for ronda in juego_controlado.historial_rondas:
        acumulado += ronda['puntos_ronda']
        assert ronda['puntos_acumulados'] == acumulado
    assert acumulado == juego_controlado.puntos


@pytest.fixture
def entradas(monkeypatch):
    # Simula lo que el usuario escribe en la terminal
    def configurar(valores):
        iterador = iter(valores)
        monkeypatch.setattr(builtins, "input", lambda *_: next(iterador))
    return configurar


def test_controlador_terminal_partida_completa(entradas, capsys):
    entradas(["x", "99", "1,2", "0", "3", "0", "1, 8"])
    repositorio = RepositorioPartidas(":memory:")
    controlador = Controlador(repositorio=repositorio, jugador="Ana")
    controlador.iniciar_juego()

    salida = capsys.readouterr().out
    assert "Formato invalido" in salida
    assert "Use numeros entre 1 y 8" in salida
    assert "FIN DEL JUEGO" in salida
    assert "Partida #1 guardada para Ana" in salida

    partidas = repositorio.ver_historial()
    assert len(partidas) == 1
    assert partidas[0]['puntos_finales'] == controlador.juego.puntos
    assert len(repositorio.ver_rondas(partidas[0]['id'])) == 5


def test_main_historial_y_exportar(tmp_path, capsys, entradas, monkeypatch):
    import main

    monkeypatch.setattr(main, "configurar_logging", lambda: None)

    bd = str(tmp_path / "p.db")
    entradas(["0"] * 5)
    main.main(["--bd", bd, "--jugador", "Luis"])
    main.main(["--bd", bd, "--historial", "--estadisticas", "--exportar", str(tmp_path / "h.csv")])
    salida = capsys.readouterr().out
    assert "HISTORIAL DE PARTIDAS" in salida and "Luis" in salida
    assert "1 partidas exportadas" in salida
    assert (tmp_path / "h.csv").read_text().startswith("id,jugador,fecha")
