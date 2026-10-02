import logging

from modelos.juego import JuegoSeguridadIoT
from vistas.vista import Vista

logger = logging.getLogger(__name__)


# Controlador que coordina logica y presentacion
class Controlador:
    def __init__(self, repositorio=None, jugador="Jugador"):
        self.juego = JuegoSeguridadIoT()
        self.vista = Vista()
        self.repositorio = repositorio
        self.jugador = jugador

    def iniciar_juego(self):
        # Inicia el ciclo completo del juego
        self._mostrar_pantalla_inicial()

        while self.juego.tiene_rondas_pendientes():
            self._ejecutar_ronda()
            self.juego.avanzar_ronda()

        self._mostrar_pantalla_final()

    def _mostrar_pantalla_inicial(self):
        # Muestra informacion inicial
        info = self.juego.get_info_inicial()
        self.vista.mostrar_bienvenida(info)

    def _ejecutar_ronda(self):
        # Ejecuta una ronda completa
        info_ronda = self.juego.get_info_ronda()
        self.vista.mostrar_encabezado_ronda(info_ronda)

        hora_ronda = self.juego.iniciar_ronda()
        alertas = self.juego.get_alertas_formateadas()
        self.vista.mostrar_alertas(alertas, hora_ronda)

        seleccion = self._obtener_y_validar_decision()
        resultados = self.juego.procesar_decisiones(seleccion)

        puntos = self.juego.puntos
        self.vista.mostrar_resultados_ronda(resultados, puntos)

    def _obtener_y_validar_decision(self):
        # Obtiene y valida la decision del jugador
        while True:
            entrada = self.vista.solicitar_decision()

            try:
                seleccion = self._parsear_entrada(entrada)

                if self.juego.validar_seleccion(seleccion):
                    return seleccion
                else:
                    total = len(self.juego.alertas_actuales)
                    self.vista.mostrar_error(f"Use numeros entre 1 y {total}")

            except ValueError:
                logger.warning("Entrada con formato invalido: %r", entrada)
                self.vista.mostrar_error("Formato invalido. Use numeros separados por comas")

    def _parsear_entrada(self, entrada):
        # Convierte entrada en lista de numeros
        if entrada == "0":
            return []
        return [int(x.strip()) for x in entrada.split(",")]

    def _mostrar_pantalla_final(self):
        # Muestra resultado final
        resultado = self.juego.get_resultado_final()
        self.vista.mostrar_resultado_final(resultado)
        self._guardar_partida()

    def _guardar_partida(self):
        # Guarda la partida si hay repositorio configurado
        if self.repositorio is None:
            return
        try:
            partida_id = self.repositorio.guardar_partida(self.juego, self.jugador)
            self.vista.mostrar_mensaje(f"Partida #{partida_id} guardada para {self.jugador}")
        except Exception:
            logger.exception("No se pudo guardar la partida")
            self.vista.mostrar_error("No se pudo guardar la partida")