"""Modelos de base de datos de la version web."""
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models, transaction
from django.utils import timezone

from modelos.juego import JuegoSeguridadIoT


class Usuario(AbstractUser):
    """Usuario del juego; extiende el usuario de Django."""

    nombre_publico = models.CharField(
        "nombre publico", max_length=40, blank=True,
        help_text="Nombre que aparece en la tabla de clasificacion.",
    )

    @property
    def nombre_visible(self):
        """Nombre publico o, si no hay, el nombre de usuario."""
        return self.nombre_publico or self.username


class Partida(models.Model):
    """Partida de un usuario, terminada o en curso."""

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                related_name="partidas")
    fecha = models.DateTimeField(default=timezone.now)
    puntos = models.IntegerField(default=JuegoSeguridadIoT.PUNTOS_INICIALES)
    victoria = models.BooleanField(default=False)
    terminada = models.BooleanField(default=False)
    ronda_actual = models.PositiveSmallIntegerField(default=1)
    alertas_pendientes = models.JSONField(
        default=list, blank=True,
        help_text="Alertas de la ronda en curso (incluye si son reales; no se muestra al jugador).",
    )

    class Meta:
        ordering = ["-fecha"]

    def __str__(self):
        estado = ("Victoria" if self.victoria else "Derrota") if self.terminada else "En curso"
        return f"Partida #{self.pk} de {self.usuario} - {self.puntos} pts ({estado})"


class Ronda(models.Model):
    """Resultado de una ronda jugada."""

    partida = models.ForeignKey(Partida, on_delete=models.CASCADE, related_name="rondas")
    numero = models.PositiveSmallIntegerField()
    hora = models.CharField(max_length=5)
    puntos = models.IntegerField(help_text="Cambio de puntos en la ronda.")
    puntos_acumulados = models.IntegerField()
    alertas_json = models.JSONField(default=list)

    class Meta:
        ordering = ["partida", "numero"]
        constraints = [
            models.UniqueConstraint(fields=["partida", "numero"], name="ronda_unica_por_partida"),
        ]

    def __str__(self):
        return f"Ronda {self.numero} de la partida #{self.partida_id}"


class Estadistica(models.Model):
    """Estadisticas acumuladas de un usuario."""

    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                   related_name="estadistica")
    total_partidas = models.PositiveIntegerField(default=0)
    victorias = models.PositiveIntegerField(default=0)
    mejor_puntuacion = models.IntegerField(null=True, blank=True)
    puntos_totales = models.IntegerField(default=0)

    class Meta:
        ordering = ["-victorias", "-mejor_puntuacion"]

    def __str__(self):
        return f"Estadisticas de {self.usuario}"

    @property
    def derrotas(self):
        """Partidas terminadas sin victoria."""
        return self.total_partidas - self.victorias

    @property
    def porcentaje_victorias(self):
        """Porcentaje de victorias con un decimal."""
        if not self.total_partidas:
            return 0.0
        return round(100 * self.victorias / self.total_partidas, 1)

    @property
    def promedio_puntos(self):
        """Puntuacion media por partida con un decimal."""
        if not self.total_partidas:
            return 0.0
        return round(self.puntos_totales / self.total_partidas, 1)

    @classmethod
    @transaction.atomic
    def registrar_partida(cls, partida):
        """
        Suma una partida terminada a las estadisticas de su usuario.

        Args:
            partida (Partida): Partida terminada.

        Returns:
            Estadistica: Estadisticas actualizadas.
        """
        estadistica, _ = cls.objects.select_for_update().get_or_create(usuario=partida.usuario)
        estadistica.total_partidas += 1
        estadistica.victorias += int(partida.victoria)
        estadistica.puntos_totales += partida.puntos
        if estadistica.mejor_puntuacion is None or partida.puntos > estadistica.mejor_puntuacion:
            estadistica.mejor_puntuacion = partida.puntos
        estadistica.save()
        return estadistica
