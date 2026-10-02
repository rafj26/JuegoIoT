import argparse
import logging

from controladores.controlador import Controlador
from modelos.persistencia import RUTA_BD_POR_DEFECTO, RepositorioPartidas
from utilidades.registro import configurar_logging
from vistas.vista import Vista


def crear_parser():
    # Define las opciones de linea de comandos
    parser = argparse.ArgumentParser(description="Sistema de Seguridad IoT (terminal)")
    parser.add_argument("--jugador", default="Jugador", help="Nombre del jugador")
    parser.add_argument("--bd", default=RUTA_BD_POR_DEFECTO, help="Ruta de la base de datos SQLite")
    parser.add_argument("--sin-guardar", action="store_true", help="No guardar la partida")
    parser.add_argument("--historial", action="store_true", help="Mostrar historial y salir")
    parser.add_argument("--estadisticas", action="store_true", help="Mostrar estadisticas y salir")
    parser.add_argument("--exportar", metavar="CSV", help="Exportar historial a CSV y salir")
    return parser


# Punto de entrada principal
def main(argv=None):
    args = crear_parser().parse_args(argv)
    configurar_logging()

    with RepositorioPartidas(args.bd) as repositorio:
        if args.historial or args.estadisticas or args.exportar:
            if args.historial:
                Vista.mostrar_historial(repositorio.ver_historial())
            if args.estadisticas:
                Vista.mostrar_estadisticas(repositorio.ver_estadisticas())
            if args.exportar:
                total = repositorio.exportar_csv(args.exportar)
                Vista.mostrar_mensaje(f"{total} partidas exportadas a {args.exportar}")
            return

        try:
            controlador = Controlador(
                repositorio=None if args.sin_guardar else repositorio,
                jugador=args.jugador,
            )
            controlador.iniciar_juego()
        except KeyboardInterrupt:
            logging.getLogger(__name__).info("Partida interrumpida por el usuario")
        except Exception:
            logging.getLogger(__name__).exception("Error inesperado durante la partida")
            raise


if __name__ == "__main__":
    main()
