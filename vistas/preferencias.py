"""Preferencias de usuario de la interfaz grafica, guardadas en JSON."""
import json
import logging
import os

logger = logging.getLogger(__name__)

RUTA_PREFERENCIAS = os.path.join("datos", "preferencias_gui.json")

VALORES_POR_DEFECTO = {
    'tema': 'oscuro',
    'pantalla_completa': False,
    'confirmar_decision': True,
    'animaciones': True,
    'jugador': 'Jugador',
    'geometria': '1000x720',
}


class Preferencias:
    """
    Preferencias de la GUI con valores por defecto.

    Args:
        ruta (str): Archivo JSON donde se guardan las preferencias.
    """

    def __init__(self, ruta=RUTA_PREFERENCIAS):
        self.ruta = ruta
        self.valores = dict(VALORES_POR_DEFECTO)
        self.cargar()

    def cargar(self):
        """Carga las preferencias del archivo, ignorando claves desconocidas."""
        try:
            with open(self.ruta, encoding="utf-8") as archivo:
                datos = json.load(archivo)
        except FileNotFoundError:
            return
        except (OSError, ValueError):
            logger.warning("Preferencias ilegibles en %s, se usan valores por defecto", self.ruta)
            return

        if isinstance(datos, dict):
            for clave, valor in datos.items():
                if clave in VALORES_POR_DEFECTO and isinstance(valor, type(VALORES_POR_DEFECTO[clave])):
                    self.valores[clave] = valor

    def guardar(self):
        """Escribe las preferencias en disco."""
        try:
            carpeta = os.path.dirname(self.ruta)
            if carpeta:
                os.makedirs(carpeta, exist_ok=True)
            with open(self.ruta, "w", encoding="utf-8") as archivo:
                json.dump(self.valores, archivo, indent=2, ensure_ascii=False)
        except OSError:
            logger.exception("No se pudieron guardar las preferencias")

    def __getitem__(self, clave):
        return self.valores[clave]

    def __setitem__(self, clave, valor):
        self.valores[clave] = valor
