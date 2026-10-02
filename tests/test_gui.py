import os

import pytest

tk = pytest.importorskip("tkinter")

from controladores.controlador_gui import ControladorGUI  # noqa: E402
from modelos.persistencia import RepositorioPartidas  # noqa: E402
from vistas.preferencias import Preferencias  # noqa: E402


@pytest.fixture
def controlador(tmp_path):
    if os.name != "nt" and not os.environ.get("DISPLAY"):
        pytest.skip("Sin pantalla disponible (usar xvfb-run)")
    try:
        root = tk.Tk()
    except tk.TclError as error:
        pytest.skip(f"Tkinter no disponible: {error}")
    prefs = Preferencias(str(tmp_path / "prefs.json"))
    prefs['confirmar_decision'] = False
    prefs['animaciones'] = False
    repo = RepositorioPartidas(":memory:")
    ctl = ControladorGUI(repositorio=repo, preferencias=prefs, root=root)
    yield ctl
    repo.cerrar()
    try:
        root.destroy()
    except tk.TclError:
        pass


def procesar_eventos(root, veces=20):
    for _ in range(veces):
        root.update()


def test_partida_completa_por_gui(controlador):
    vista, root = controlador.vista, controlador.root
    controlador.preparar_partida()
    vista.var_jugador.set("Tester")
    vista._tecla_enter()

    for numero in range(1, 6):
        procesar_eventos(root)
        assert controlador.juego.ronda_actual == numero
        assert len(vista.cards) == 8
        vista.alternar_alerta(1)
        vista.alternar_alerta(2)
        vista.alternar_alerta(2)
        assert vista.seleccion == {1}
        vista._tecla_enter()
        procesar_eventos(root)
        assert len(controlador.historial_puntos) == numero + 1
        vista._tecla_enter()

    procesar_eventos(root)
    assert not controlador.juego.tiene_rondas_pendientes()
    assert vista.label_estado.cget("text") == "Partida #1 guardada para Tester"
    assert controlador.repositorio.ver_historial()[0]['jugador'] == "Tester"


def test_pausa_bloquea_entradas(controlador):
    vista, root = controlador.vista, controlador.root
    controlador.preparar_partida()
    vista._tecla_enter()
    procesar_eventos(root)
    vista.alternar_pausa()
    vista.alternar_alerta(1)
    vista._tecla_enter()
    assert vista.seleccion == set()
    assert controlador.juego.historial_rondas == []
    vista.alternar_pausa()
    vista.alternar_alerta(1)
    assert vista.seleccion == {1}


def test_cambiar_tema_conserva_seleccion_y_guarda_preferencia(controlador):
    vista, root = controlador.vista, controlador.root
    controlador.preparar_partida()
    vista._tecla_enter()
    procesar_eventos(root)
    vista.alternar_alerta(3)
    vista.alternar_tema()
    procesar_eventos(root)
    assert vista.prefs['tema'] == 'claro'
    assert vista.seleccion == {3}
    assert len(vista.cards) == 8
    assert Preferencias(vista.prefs.ruta)['tema'] == 'claro'
