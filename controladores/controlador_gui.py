"""Controlador de la version grafica."""
import logging
import tkinter as tk

from modelos.juego import JuegoSeguridadIoT
from vistas.preferencias import Preferencias
from vistas.vista_gui import VistaGUI

logger = logging.getLogger(__name__)


class ControladorGUI:
    """
    Controlador para interfaz grafica (dirigido por eventos de Tkinter).

    Args:
        repositorio (RepositorioPartidas, optional): Donde guardar las partidas.
        preferencias (Preferencias, optional): Preferencias de la GUI.
        root (tk.Tk, optional): Ventana principal; se crea si no se indica.
    """

    def __init__(self, repositorio=None, preferencias=None, root=None):
        """Crea la ventana y la vista grafica."""
        self.root = root or tk.Tk()
        self.repositorio = repositorio
        self.vista = VistaGUI(self.root, preferencias or Preferencias())
        self.jugador = self.vista.prefs['jugador']
        self.juego = None
        self.historial_puntos = []

    def iniciar_juego(self):
        """Muestra la bienvenida e inicia el loop de Tkinter."""
        self.preparar_partida()
        self.root.mainloop()

    def preparar_partida(self):
        """Crea una partida nueva y muestra la pantalla inicial."""
        self.juego = JuegoSeguridadIoT()
        self.historial_puntos = [self.juego.puntos]
        info = self.juego.get_info_inicial()
        self.vista.mostrar_bienvenida(info, self._comenzar)

    def _comenzar(self, jugador):
        """El jugador pulso comenzar en la bienvenida."""
        self.jugador = jugador
        logger.info("Partida GUI iniciada por %s", jugador)
        self._siguiente_ronda()

    def _siguiente_ronda(self):
        """Muestra la transicion y despues las alertas de la ronda."""
        numero = self.juego.ronda_actual
        self.vista.mostrar_transicion(numero, self._ejecutar_ronda)

    def _ejecutar_ronda(self):
        """Genera las alertas y espera la decision del jugador."""
        info_ronda = self.juego.get_info_ronda()
        self.vista.actualizar_info_ronda(info_ronda)

        hora_ronda = self.juego.iniciar_ronda()
        alertas = self.juego.get_alertas_formateadas()
        self.vista.mostrar_alertas(alertas, hora_ronda, self._procesar_decision)

    def _procesar_decision(self, seleccion):
        """Evalua las decisiones del jugador y muestra resultados."""
        if not self.juego.validar_seleccion(seleccion):
            self.vista.mostrar_estado("Seleccion invalida", 'error')
            return

        resultados = self.juego.procesar_decisiones(seleccion)
        self.historial_puntos.append(self.juego.puntos)
        self.vista.mostrar_resultados_ronda(resultados, self.juego.puntos,
                                            list(self.historial_puntos), self._continuar)

    def _continuar(self):
        """Avanza a la siguiente ronda o termina la partida."""
        self.juego.avanzar_ronda()
        if self.juego.tiene_rondas_pendientes():
            self._siguiente_ronda()
        else:
            self._mostrar_pantalla_final()

    def _mostrar_pantalla_final(self):
        """Muestra resultado final y guarda la partida."""
        resultado = self.juego.get_resultado_final()
        mensaje = self._guardar_partida()
        self.vista.mostrar_resultado_final(resultado, list(self.historial_puntos),
                                           self.preparar_partida, mensaje)

    def _guardar_partida(self):
        """Guarda la partida y devuelve (mensaje, tipo) para la barra de estado."""
        if self.repositorio is None:
            return None
        try:
            partida_id = self.repositorio.guardar_partida(self.juego, self.jugador)
            return (f"Partida #{partida_id} guardada para {self.jugador}", 'exito')
        except Exception:
            logger.exception("No se pudo guardar la partida")
            return ("No se pudo guardar la partida", 'error')
