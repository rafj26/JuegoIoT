import logging

from controladores.controlador import Controlador
from utilidades.registro import configurar_logging

# Punto de entrada principal
def main():
    configurar_logging()
    try:
        controlador = Controlador()
        controlador.iniciar_juego()
    except KeyboardInterrupt:
        logging.getLogger(__name__).info("Partida interrumpida por el usuario")
    except Exception:
        logging.getLogger(__name__).exception("Error inesperado durante la partida")
        raise

if __name__ == "__main__":
    main()