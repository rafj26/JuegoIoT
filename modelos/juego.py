from datetime import datetime, timedelta
from modelos.red_iot import RedIoT


# Clase principal del juego - solo logica de negocio
class JuegoSeguridadIoT:
    PUNTOS_INICIALES = 15
    TOTAL_RONDAS = 5
    PUNTOS_VICTORIA = 15
    PUNTOS_ALERTA_REAL_ATENDIDA = 2
    PUNTOS_ALERTA_FALSA_ATENDIDA = -1
    PUNTOS_ALERTA_REAL_NO_ATENDIDA = -2
    PUNTOS_ALERTA_FALSA_NO_ATENDIDA = 0

    def __init__(self):
        self.puntos = self.PUNTOS_INICIALES
        self.ronda_actual = 1
        self.red = RedIoT()
        self.hora_inicio = datetime.now().replace(hour=8, minute=0, second=0)
        self.alertas_actuales = []

    def get_info_inicial(self):
        # Retorna informacion inicial del juego
        return {
            'puntos_iniciales': self.PUNTOS_INICIALES,
            'total_rondas': self.TOTAL_RONDAS,
            'puntos_victoria': self.PUNTOS_VICTORIA,
            'reglas': self._get_reglas()
        }

    def _get_reglas(self):
        # Retorna las reglas del juego
        return {
            'alerta_real_atendida': self.PUNTOS_ALERTA_REAL_ATENDIDA,
            'alerta_falsa_atendida': self.PUNTOS_ALERTA_FALSA_ATENDIDA,
            'alerta_real_no_atendida': self.PUNTOS_ALERTA_REAL_NO_ATENDIDA,
            'alerta_falsa_no_atendida': self.PUNTOS_ALERTA_FALSA_NO_ATENDIDA
        }

    def tiene_rondas_pendientes(self):
        # Verifica si quedan rondas por jugar
        return self.ronda_actual <= self.TOTAL_RONDAS

    def get_info_ronda(self):
        # Retorna informacion de la ronda actual
        return {
            'numero': self.ronda_actual,
            'total': self.TOTAL_RONDAS,
            'puntos': self.puntos
        }

    def iniciar_ronda(self):
        # Inicia una nueva ronda y genera alertas
        hora_ronda = self._calcular_hora_ronda()
        self.alertas_actuales = self.red.generar_alertas_turno(hora_ronda)
        return hora_ronda

    def _calcular_hora_ronda(self):
        # Calcula la hora de la ronda actual
        horas_transcurridas = (self.ronda_actual - 1) * 3
        return self.hora_inicio + timedelta(hours=horas_transcurridas)

    def get_alertas_formateadas(self):
        # Retorna lista de alertas formateadas
        return [alerta.get_info_formateada(i)
                for i, alerta in enumerate(self.alertas_actuales, 1)]

    def validar_seleccion(self, numeros):
        # Valida que los numeros esten en rango
        if not numeros:
            return True
        total = len(self.alertas_actuales)
        return all(1 <= num <= total for num in numeros)

    def procesar_decisiones(self, seleccion):
        # Procesa las decisiones y retorna resultados
        resultados = []

        for i, alerta in enumerate(self.alertas_actuales, 1):
            atendida = i in seleccion
            cambio = self._calcular_cambio_puntos(alerta, atendida)
            self.puntos += cambio

            resultado = {
                'indice': i,
                'atendida': atendida,
                'es_real': alerta.es_real,
                'cambio_puntos': cambio,
                'descripcion': self._get_descripcion_resultado(alerta, atendida)
            }
            resultados.append(resultado)

        return resultados

    def _calcular_cambio_puntos(self, alerta, atendida):
        # Calcula cambio de puntos segun reglas
        if atendida and alerta.es_real:
            return self.PUNTOS_ALERTA_REAL_ATENDIDA
        elif atendida and not alerta.es_real:
            return self.PUNTOS_ALERTA_FALSA_ATENDIDA
        elif not atendida and alerta.es_real:
            return self.PUNTOS_ALERTA_REAL_NO_ATENDIDA
        else:
            return self.PUNTOS_ALERTA_FALSA_NO_ATENDIDA

    def _get_descripcion_resultado(self, alerta, atendida):
        # Retorna descripcion del resultado
        if atendida and alerta.es_real:
            return "Correcto - Alerta real atendida"
        elif atendida and not alerta.es_real:
            return "Falsa alarma atendida"
        elif not atendida and alerta.es_real:
            return "Error - Alerta real ignorada"
        else:
            return "Correcto - Falsa alarma ignorada"

    def avanzar_ronda(self):
        # Avanza a la siguiente ronda
        self.ronda_actual += 1

    def get_resultado_final(self):
        # Retorna resultado final del juego
        victoria = self.puntos >= self.PUNTOS_VICTORIA
        return {
            'puntos_finales': self.puntos,
            'victoria': victoria,
            'mensaje': self._get_mensaje_final(victoria)
        }

    def _get_mensaje_final(self, victoria):
        # Retorna mensaje final segun resultado
        if victoria:
            return "Has mantenido la seguridad de la red"
        else:
            return "La seguridad de la red ha sido comprometida"