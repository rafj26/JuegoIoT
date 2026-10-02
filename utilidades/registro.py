"""Configuracion centralizada del sistema de logging."""
import logging
import os

RUTA_LOG_POR_DEFECTO = os.path.join("logs", "juego.log")
FORMATO = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"


def configurar_logging(ruta=RUTA_LOG_POR_DEFECTO, nivel=logging.INFO):
    """
    Configura el logger raiz para escribir en un archivo.

    Crea la carpeta del archivo si no existe. Llamarla varias veces no
    duplica los handlers.

    Args:
        ruta (str): Ruta del archivo de log.
        nivel (int): Nivel minimo de los mensajes registrados.

    Returns:
        logging.Logger: Logger raiz configurado.
    """
    carpeta = os.path.dirname(ruta)
    if carpeta:
        os.makedirs(carpeta, exist_ok=True)

    raiz = logging.getLogger()
    raiz.setLevel(nivel)

    ruta_absoluta = os.path.abspath(ruta)
    for handler in raiz.handlers:
        if getattr(handler, "baseFilename", None) == ruta_absoluta:
            return raiz

    handler = logging.FileHandler(ruta, encoding="utf-8")
    handler.setFormatter(logging.Formatter(FORMATO))
    raiz.addHandler(handler)
    return raiz
