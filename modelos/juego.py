"""Logica principal del juego: rondas, puntuacion y resultado."""
import logging
from datetime import datetime, timedelta

from modelos.red_iot import RedIoT

logger = logging.getLogger(__name__)


class JuegoSeguridadIoT:
    """
    Clase principal del juego - solo logica de negocio.

    No imprime nada: devuelve diccionarios que las vistas presentan.

    Attributes:
        puntos (int): Puntuacion actual.
        ronda_actual (int): Numero de la ronda en curso (desde 1).
        red (RedIoT): Red de dispositivos que genera las alertas.
        alertas_actuales (list[Alerta]): Alertas de la ronda en curso.
        historial_rondas (list[dict]): Resumen de cada ronda jugada.
    """

    PUNTOS_INICIALES = 15
    TOTAL_RONDAS = 5
    PUNTOS_VICTORIA = 15
    PUNTOS_ALERTA_REAL_ATENDIDA = 2
    PUNTOS_ALERTA_FALSA_ATENDIDA = -1
    PUNTOS_ALERTA_REAL_NO_ATENDIDA = -2
    PUNTOS_ALERTA_FALSA_NO_ATENDIDA = 0

    def __init__(self):
        """Inicializa el estado."""
        self.puntos = self.PUNTOS_INICIALES
        self.ronda_actual = 1
        self.red = RedIoT()
        self.hora_inicio = datetime.now().replace(hour=8, minute=0, second=0)
        self.alertas_actuales = []
        self.hora_ronda_actual = None
        self.historial_rondas = []
        logger.info("Nueva partida creada con %d puntos", self.puntos)

    @classmethod
    def get_info_inicial(cls):
        """
        Retorna informacion inicial del juego.

        Returns:
            dict: ``puntos_iniciales``, ``total_rondas``, ``puntos_victoria``
            y ``reglas`` (puntos por cada tipo de decision).
        """
        return {
            'puntos_iniciales': cls.PUNTOS_INICIALES,
            'total_rondas': cls.TOTAL_RONDAS,
            'puntos_victoria': cls.PUNTOS_VICTORIA,
            'reglas': cls._get_reglas()
        }

    @classmethod
    def _get_reglas(cls):
        """Retorna las reglas del juego."""
        return {
            'alerta_real_atendida': cls.PUNTOS_ALERTA_REAL_ATENDIDA,
            'alerta_falsa_atendida': cls.PUNTOS_ALERTA_FALSA_ATENDIDA,
            'alerta_real_no_atendida': cls.PUNTOS_ALERTA_REAL_NO_ATENDIDA,
            'alerta_falsa_no_atendida': cls.PUNTOS_ALERTA_FALSA_NO_ATENDIDA
        }

    def tiene_rondas_pendientes(self):
        """
        Verifica si quedan rondas por jugar.

        Returns:
            bool: ``True`` mientras no se hayan jugado todas las rondas.
        """
        return self.ronda_actual <= self.TOTAL_RONDAS

    def get_info_ronda(self):
        """
        Retorna informacion de la ronda actual.

        Returns:
            dict: ``numero``, ``total`` y ``puntos``.
        """
        return {
            'numero': self.ronda_actual,
            'total': self.TOTAL_RONDAS,
            'puntos': self.puntos
        }

    def iniciar_ronda(self):
        """
        Inicia una nueva ronda y genera alertas.

        Returns:
            datetime: Hora simulada de la ronda.
        """
        hora_ronda = self._calcular_hora_ronda()
        self.hora_ronda_actual = hora_ronda
        self.alertas_actuales = self.red.generar_alertas_turno(hora_ronda)
        reales = sum(1 for alerta in self.alertas_actuales if alerta.es_real)
        logger.info("Ronda %d iniciada a las %s: %d alertas (%d reales)",
                    self.ronda_actual, hora_ronda.strftime("%H:%M"),
                    len(self.alertas_actuales), reales)
        return hora_ronda

    def _calcular_hora_ronda(self):
        """Calcula la hora de la ronda actual."""
        horas_transcurridas = (self.ronda_actual - 1) * 3
        return self.hora_inicio + timedelta(hours=horas_transcurridas)

    def get_alertas_formateadas(self):
        """
        Retorna lista de alertas formateadas.

        Returns:
            list[dict]: Informacion visible de cada alerta, numerada desde 1.
        """
        return [alerta.get_info_formateada(i)
                for i, alerta in enumerate(self.alertas_actuales, 1)]

    def validar_seleccion(self, numeros):
        """
        Valida que los numeros esten en rango.

        Args:
            numeros (list[int]): Indices de alertas elegidas (desde 1).

        Returns:
            bool: ``True`` si la lista esta vacia o todos los indices existen.
        """
        if not numeros:
            return True
        total = len(self.alertas_actuales)
        valida = all(1 <= num <= total for num in numeros)
        if not valida:
            logger.warning("Seleccion fuera de rango: %s (total %d)", numeros, total)
        return valida

    def procesar_decisiones(self, seleccion):
        """
        Procesa las decisiones y retorna resultados.

        Actualiza los puntos y agrega la ronda a ``historial_rondas``.

        Args:
            seleccion (list[int]): Indices de las alertas atendidas; las
                demas se consideran ignoradas.

        Returns:
            list[dict]: Por alerta: ``indice``, ``atendida``, ``es_real``,
            ``cambio_puntos`` y ``descripcion``.
        """
        resultados = []
        logger.info("Ronda %d - alertas atendidas: %s",
                    self.ronda_actual, sorted(seleccion) or "ninguna")

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
            logger.debug("Alerta %d (%s): atendida=%s real=%s cambio=%+d",
                         i, alerta.dispositivo.id, atendida, alerta.es_real, cambio)

        cambio_ronda = sum(r['cambio_puntos'] for r in resultados)
        logger.info("Ronda %d - cambio de puntos: %+d, total: %d",
                    self.ronda_actual, cambio_ronda, self.puntos)
        self._registrar_ronda(resultados, cambio_ronda)
        return resultados

    def _registrar_ronda(self, resultados, cambio_ronda):
        """Guarda el resumen de la ronda para el historial de la partida."""
        alertas = []
        for alerta, resultado in zip(self.alertas_actuales, resultados):
            info = alerta.get_info_formateada(resultado['indice'])
            info.update({
                'es_real': alerta.es_real,
                'atendida': resultado['atendida'],
                'cambio_puntos': resultado['cambio_puntos'],
            })
            alertas.append(info)

        hora = self.hora_ronda_actual.strftime("%H:%M") if self.hora_ronda_actual else ""
        self.historial_rondas.append({
            'numero': self.ronda_actual,
            'hora': hora,
            'puntos_ronda': cambio_ronda,
            'puntos_acumulados': self.puntos,
            'alertas': alertas,
        })

    def _calcular_cambio_puntos(self, alerta, atendida):
        """
        Calcula cambio de puntos segun reglas.

        Args:
            alerta (Alerta): Alerta a evaluar.
            atendida (bool): Si fue atendida.

        Returns:
            int: Cambio de puntos (-2, -1, 0, +2).
        """
        if atendida and alerta.es_real:
            return self.PUNTOS_ALERTA_REAL_ATENDIDA
        elif atendida and not alerta.es_real:
            return self.PUNTOS_ALERTA_FALSA_ATENDIDA
        elif not atendida and alerta.es_real:
            return self.PUNTOS_ALERTA_REAL_NO_ATENDIDA
        else:
            return self.PUNTOS_ALERTA_FALSA_NO_ATENDIDA

    def _get_descripcion_resultado(self, alerta, atendida):
        """Retorna descripcion del resultado."""
        if atendida and alerta.es_real:
            return "Correcto - Alerta real atendida"
        elif atendida and not alerta.es_real:
            return "Falsa alarma atendida"
        elif not atendida and alerta.es_real:
            return "Error - Alerta real ignorada"
        else:
            return "Correcto - Falsa alarma ignorada"

    def avanzar_ronda(self):
        """Avanza a la siguiente ronda."""
        self.ronda_actual += 1

    def get_resultado_final(self):
        """
        Retorna resultado final del juego.

        Returns:
            dict: ``puntos_finales``, ``victoria`` y ``mensaje``.
        """
        victoria = self.puntos >= self.PUNTOS_VICTORIA
        logger.info("Partida terminada: %d puntos, %s",
                    self.puntos, "victoria" if victoria else "derrota")
        return {
            'puntos_finales': self.puntos,
            'victoria': victoria,
            'mensaje': self.get_mensaje_final(victoria)
        }

    @staticmethod
    def get_mensaje_final(victoria):
        """
        Retorna mensaje final segun resultado.

        Args:
            victoria (bool): Si el jugador gano.

        Returns:
            str: Mensaje para la pantalla final.
        """
        if victoria:
            return "Has mantenido la seguridad de la red"
        else:
            return "La seguridad de la red ha sido comprometida"
