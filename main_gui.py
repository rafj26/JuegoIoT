import logging

from controladores.controlador_gui import ControladorGUI
from utilidades.registro import configurar_logging

# Punto de entrada con interfaz grafica
def main():
    configurar_logging()
    try:
        controlador = ControladorGUI()
        controlador.iniciar_juego()
    except KeyboardInterrupt:
        logging.getLogger(__name__).info("Partida interrumpida por el usuario")
    except Exception:
        logging.getLogger(__name__).exception("Error inesperado durante la partida")
        raise

if __name__ == "__main__":
    main()