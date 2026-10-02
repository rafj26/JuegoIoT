"""Punto de entrada de la version grafica."""
import logging

from controladores.controlador_gui import ControladorGUI
from modelos.persistencia import RepositorioPartidas
from utilidades.registro import configurar_logging


def main():
    """Configura el logging y abre la version grafica."""
    configurar_logging()
    try:
        with RepositorioPartidas() as repositorio:
            controlador = ControladorGUI(repositorio=repositorio)
            controlador.iniciar_juego()
    except KeyboardInterrupt:
        logging.getLogger(__name__).info("Partida interrumpida por el usuario")
    except Exception:
        logging.getLogger(__name__).exception("Error inesperado durante la partida")
        raise


if __name__ == "__main__":
    main()
