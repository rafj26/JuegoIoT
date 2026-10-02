import tkinter as tk
from modelos.juego import JuegoSeguridadIoT
from vistas.vista_gui import VistaGUI


# Controlador para interfaz grafica
class ControladorGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.juego = JuegoSeguridadIoT()
        self.vista = VistaGUI(self.root)

    def iniciar_juego(self):
        # Muestra pantalla inicial
        self._mostrar_pantalla_inicial()

        # Ciclo principal del juego
        while self.juego.tiene_rondas_pendientes():
            self._ejecutar_ronda()
            self.juego.avanzar_ronda()

        # Muestra resultado final
        self._mostrar_pantalla_final()

        # Inicia loop de tkinter
        self.root.mainloop()

    def _mostrar_pantalla_inicial(self):
        # Muestra informacion inicial
        info = self.juego.get_info_inicial()
        self.vista.mostrar_bienvenida(info)

    def _ejecutar_ronda(self):
        # Actualiza informacion de ronda
        info_ronda = self.juego.get_info_ronda()
        self.vista.actualizar_info_ronda(info_ronda)

        # Genera y muestra alertas
        hora_ronda = self.juego.iniciar_ronda()
        alertas = self.juego.get_alertas_formateadas()
        self.vista.mostrar_alertas(alertas, hora_ronda)

        # Espera decision del jugador
        seleccion = self._obtener_decision()

        # Procesa decisiones
        resultados = self.juego.procesar_decisiones(seleccion)
        puntos = self.juego.puntos

        # Muestra resultados
        self.vista.mostrar_resultados_ronda(resultados, puntos)
        self.vista.esperar_continuar()

    def _obtener_decision(self):
        # Espera a que el jugador tome decision
        while not self.vista.esta_decision_tomada():
            self.vista.actualizar()

        return self.vista.obtener_decision()

    def _mostrar_pantalla_final(self):
        # Muestra resultado final
        resultado = self.juego.get_resultado_final()
        self.vista.mostrar_resultado_final(resultado)