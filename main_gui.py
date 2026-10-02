from controladores.controlador_gui import ControladorGUI

# Punto de entrada con interfaz grafica
def main():
    controlador = ControladorGUI()
    controlador.iniciar_juego()

if __name__ == "__main__":
    main()