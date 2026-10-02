import json
import logging

import pytest

from utilidades.registro import configurar_logging
from vistas.preferencias import VALORES_POR_DEFECTO, Preferencias


@pytest.fixture
def raiz_limpia():
    raiz = logging.getLogger()
    previos = list(raiz.handlers)
    nivel = raiz.level
    yield raiz
    for handler in list(raiz.handlers):
        if handler not in previos:
            handler.close()
            raiz.removeHandler(handler)
    raiz.setLevel(nivel)


def test_configurar_logging_escribe_archivo(tmp_path, raiz_limpia, juego):
    ruta = tmp_path / "logs" / "juego.log"
    configurar_logging(str(ruta))
    configurar_logging(str(ruta))  # no duplica handlers
    juego.iniciar_ronda()
    juego.procesar_decisiones([1])
    for handler in raiz_limpia.handlers:
        handler.flush()
    contenido = ruta.read_text(encoding="utf-8")
    assert "Ronda 1 iniciada" in contenido
    assert "alertas atendidas: [1]" in contenido
    assert contenido.count("Ronda 1 iniciada") == 1


def test_preferencias_por_defecto(tmp_path):
    prefs = Preferencias(str(tmp_path / "prefs.json"))
    assert prefs.valores == VALORES_POR_DEFECTO


def test_preferencias_guardar_y_cargar(tmp_path):
    ruta = str(tmp_path / "sub" / "prefs.json")
    prefs = Preferencias(ruta)
    prefs['tema'] = 'claro'
    prefs['jugador'] = 'Ana'
    prefs.guardar()
    otra = Preferencias(ruta)
    assert otra['tema'] == 'claro' and otra['jugador'] == 'Ana'


def test_preferencias_ignoran_valores_invalidos(tmp_path):
    ruta = tmp_path / "prefs.json"
    ruta.write_text(json.dumps({'tema': 3, 'desconocida': 1, 'animaciones': False}))
    prefs = Preferencias(str(ruta))
    assert prefs['tema'] == VALORES_POR_DEFECTO['tema']
    assert prefs['animaciones'] is False
    assert 'desconocida' not in prefs.valores


def test_preferencias_archivo_corrupto(tmp_path):
    ruta = tmp_path / "prefs.json"
    ruta.write_text("{no es json")
    assert Preferencias(str(ruta)).valores == VALORES_POR_DEFECTO
