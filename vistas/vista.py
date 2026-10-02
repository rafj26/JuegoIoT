"""Vista de terminal del juego."""


class Vista:
    """Clase para manejar toda la presentacion."""

    @staticmethod
    def mostrar_bienvenida(info_inicial):
        """Muestra pantalla inicial."""
        print("=" * 60)
        print("SISTEMA DE SEGURIDAD IoT - ADMINISTRADOR DE REDES")
        print("=" * 60)
        print(f"Puntos iniciales: {info_inicial['puntos_iniciales']}")
        print(f"Rondas totales: {info_inicial['total_rondas']}")
        print(f"\nObjetivo: Mantener {info_inicial['puntos_victoria']} o mas puntos")
        print("\nReglas de puntuacion:")
        reglas = info_inicial['reglas']
        print(f"  Alerta real atendida: +{reglas['alerta_real_atendida']} puntos")
        print(f"  Alerta falsa atendida: {reglas['alerta_falsa_atendida']} punto")
        print(f"  Alerta real NO atendida: {reglas['alerta_real_no_atendida']} puntos")
        print(f"  Alerta falsa NO atendida: {reglas['alerta_falsa_no_atendida']} puntos")
        print("=" * 60)

    @staticmethod
    def mostrar_encabezado_ronda(info_ronda):
        """Muestra informacion de ronda."""
        print(f"\n{'=' * 60}")
        print(f"RONDA {info_ronda['numero']}/{info_ronda['total']}")
        print(f"Puntos actuales: {info_ronda['puntos']}")
        print("=" * 60)

    @staticmethod
    def mostrar_alertas(alertas, hora):
        """Muestra todas las alertas."""
        print(f"\nAlertas detectadas a las {hora.strftime('%H:%M')}:")
        print("-" * 60)

        for alerta in alertas:
            Vista._mostrar_alerta_individual(alerta)
            print("-" * 60)

    @staticmethod
    def _mostrar_alerta_individual(info):
        """Muestra una alerta individual."""
        print(f"[{info['indice']}] {info['hora']} | {info['tipo']}")
        print(f"    Ubicacion: {info['ubicacion']}")
        print(f"    Alerta: {info['mensaje']}")
        print(f"    ID: {info['id']}")

    @staticmethod
    def solicitar_decision():
        """Solicita decision al usuario."""
        print("\nIngrese numeros de alertas a atender (separados por comas)")
        print("O ingrese 0 para no atender ninguna:")
        return input("> ").strip()

    @staticmethod
    def mostrar_error(mensaje):
        """Muestra mensaje de error."""
        print(f"Error: {mensaje}")

    @staticmethod
    def mostrar_resultados_ronda(resultados, puntos_totales):
        """Muestra resultados de la ronda."""
        print("\n" + "=" * 60)
        print("RESULTADO DE LA RONDA:")
        print("=" * 60)

        for resultado in resultados:
            Vista._mostrar_resultado_individual(resultado)

        print("=" * 60)
        print(f"Puntos totales: {puntos_totales}")

    @staticmethod
    def _mostrar_resultado_individual(resultado):
        """Muestra resultado individual."""
        accion = "ATENDIDA" if resultado['atendida'] else "IGNORADA"
        tipo = "REAL" if resultado['es_real'] else "FALSA"
        cambio = resultado['cambio_puntos']
        signo = "+" if cambio > 0 else ""

        print(f"[{resultado['indice']}] {accion} | {tipo} | "
              f"{signo}{cambio} pts | {resultado['descripcion']}")

    @staticmethod
    def mostrar_resultado_final(resultado):
        """Muestra pantalla final."""
        print("\n" + "=" * 60)
        print("FIN DEL JUEGO")
        print("=" * 60)
        print(f"Puntuacion final: {resultado['puntos_finales']} puntos")

        if resultado['victoria']:
            print("\nVICTORIA")
        else:
            print("\nDERROTA")

        print(resultado['mensaje'])
        print("=" * 60)

    @staticmethod
    def mostrar_mensaje(mensaje):
        """Muestra un mensaje informativo."""
        print(mensaje)

    @staticmethod
    def mostrar_historial(partidas):
        """Muestra la lista de partidas guardadas."""
        print("=" * 60)
        print("HISTORIAL DE PARTIDAS")
        print("=" * 60)
        if not partidas:
            print("No hay partidas guardadas")
            return
        print(f"{'#':>4}  {'Fecha':<19}  {'Jugador':<15} {'Puntos':>6}  Resultado")
        print("-" * 60)
        for p in partidas:
            resultado = "VICTORIA" if p['victoria'] else "DERROTA"
            print(f"{p['id']:>4}  {p['fecha']:<19}  {p['jugador'][:15]:<15} "
                  f"{p['puntos_finales']:>6}  {resultado}")

    @staticmethod
    def mostrar_estadisticas(estadisticas):
        """Muestra las estadisticas por jugador."""
        print("=" * 60)
        print("ESTADISTICAS")
        print("=" * 60)
        if not estadisticas:
            print("No hay estadisticas todavia")
            return
        for e in estadisticas:
            print(f"Jugador: {e['jugador']}")
            print(f"  Partidas: {e['total_partidas']}  "
                  f"Victorias: {e['victorias']} ({e['porcentaje_victorias']}%)  "
                  f"Derrotas: {e['derrotas']}")
            print(f"  Mejor puntuacion: {e['mejor_puntuacion']}  "
                  f"Promedio: {e['promedio_puntos']}")
            print("-" * 60)
