"""
Adaptador entre la logica existente (modelos.juego) y la base de datos.

Cada peticion HTTP reconstruye un JuegoSeguridadIoT a partir de la Partida
guardada, usa sus metodos para generar alertas y calcular puntos, y guarda
el nuevo estado.
"""
from datetime import datetime

from django.db import transaction
from django.utils import timezone

from juego_app.models import Estadistica, Ronda
from modelos.alerta import Alerta
from modelos.juego import JuegoSeguridadIoT


class SeleccionInvalida(ValueError):
    """La seleccion de alertas no es valida para la ronda actual."""


class AdaptadorJuego:
    """
    Reconstruye y persiste el estado de una partida.

    Args:
        partida (Partida): Partida guardada en la base de datos.
    """

    def __init__(self, partida):
        """Reconstruye el juego a partir de la partida."""
        self.partida = partida
        self.juego = JuegoSeguridadIoT()
        self.juego.puntos = partida.puntos
        self.juego.ronda_actual = partida.ronda_actual
        fecha = timezone.localtime(partida.fecha) if timezone.is_aware(partida.fecha) else partida.fecha
        self.juego.hora_inicio = fecha.replace(hour=8, minute=0, second=0, microsecond=0, tzinfo=None)
        self.juego.alertas_actuales = self._restaurar_alertas(partida.alertas_pendientes)
        if self.juego.alertas_actuales:
            self.juego.hora_ronda_actual = self.juego.alertas_actuales[0].hora

    @property
    def tiene_rondas_pendientes(self):
        """Indica si quedan rondas por jugar."""
        return self.juego.tiene_rondas_pendientes()

    def iniciar_ronda(self):
        """
        Genera las alertas de la ronda actual si aun no existen.

        Returns:
            datetime: Hora simulada de la ronda.
        """
        if not self.juego.alertas_actuales:
            self.juego.iniciar_ronda()
            self.partida.alertas_pendientes = self._serializar_alertas(self.juego.alertas_actuales)
            self.partida.save(update_fields=["alertas_pendientes"])
        return self.juego.alertas_actuales[0].hora

    def get_alertas(self):
        """
        Devuelve las alertas visibles de la ronda (sin indicar si son reales).

        Returns:
            list[dict]: Alertas formateadas por el modelo del juego.
        """
        return self.juego.get_alertas_formateadas()

    def get_info_ronda(self):
        """Devuelve numero de ronda, total y puntos."""
        return self.juego.get_info_ronda()

    @transaction.atomic
    def procesar(self, seleccion):
        """
        Aplica las decisiones del jugador y guarda la ronda.

        Args:
            seleccion (list[int]): Indices de alertas atendidas.

        Returns:
            Ronda: Ronda guardada con sus resultados.

        Raises:
            SeleccionInvalida: Si no hay ronda en curso o los indices no existen.
        """
        if not self.juego.alertas_actuales or self.partida.terminada:
            raise SeleccionInvalida("No hay una ronda en curso")
        if not self.juego.validar_seleccion(seleccion):
            raise SeleccionInvalida("Hay alertas seleccionadas que no existen")

        resultados = self.juego.procesar_decisiones(sorted(set(seleccion)))
        resumen = self.juego.historial_rondas[-1]
        for alerta, resultado in zip(resumen['alertas'], resultados):
            alerta['descripcion'] = resultado['descripcion']

        ronda = Ronda.objects.create(
            partida=self.partida,
            numero=resumen['numero'],
            hora=resumen['hora'],
            puntos=resumen['puntos_ronda'],
            puntos_acumulados=resumen['puntos_acumulados'],
            alertas_json=resumen['alertas'],
        )

        self.juego.avanzar_ronda()
        self.partida.puntos = self.juego.puntos
        self.partida.ronda_actual = self.juego.ronda_actual
        self.partida.alertas_pendientes = []

        if not self.juego.tiene_rondas_pendientes():
            self.partida.terminada = True
            self.partida.victoria = self.juego.get_resultado_final()['victoria']
            self.partida.save()
            Estadistica.registrar_partida(self.partida)
        else:
            self.partida.save()
        return ronda

    @staticmethod
    def _serializar_alertas(alertas):
        """Convierte las alertas en datos JSON."""
        return [
            {
                'dispositivo_id': alerta.dispositivo.id,
                'mensaje': alerta.mensaje,
                'es_real': alerta.es_real,
                'hora': alerta.hora.isoformat(),
            }
            for alerta in alertas
        ]

    def _restaurar_alertas(self, datos):
        """Reconstruye objetos Alerta a partir de los datos JSON."""
        dispositivos = {d.id: d for d in self.juego.red.dispositivos}
        return [
            Alerta(dispositivos[d['dispositivo_id']], d['mensaje'], d['es_real'],
                   datetime.fromisoformat(d['hora']))
            for d in datos
        ]
