"""Serializadores de la API REST."""
from rest_framework import serializers

from juego_app.models import Estadistica, Partida, Ronda


class RondaSerializer(serializers.ModelSerializer):
    """Ronda jugada con el detalle de sus alertas."""

    alertas = serializers.JSONField(source="alertas_json", read_only=True)

    class Meta:
        model = Ronda
        fields = ("id", "partida", "numero", "hora", "puntos", "puntos_acumulados", "alertas")
        read_only_fields = fields


class PartidaSerializer(serializers.ModelSerializer):
    """Resumen de una partida."""

    rondas_jugadas = serializers.IntegerField(source="rondas.count", read_only=True)

    class Meta:
        model = Partida
        fields = ("id", "fecha", "puntos", "victoria", "terminada", "ronda_actual", "rondas_jugadas")
        read_only_fields = fields


class PartidaDetalleSerializer(PartidaSerializer):
    """Partida con todas sus rondas."""

    rondas = RondaSerializer(many=True, read_only=True)

    class Meta(PartidaSerializer.Meta):
        fields = PartidaSerializer.Meta.fields + ("rondas",)
        read_only_fields = fields


class AlertaSerializer(serializers.Serializer):
    """Alerta visible de la ronda en curso (no indica si es real)."""

    indice = serializers.IntegerField()
    hora = serializers.CharField()
    tipo = serializers.CharField()
    ubicacion = serializers.CharField()
    mensaje = serializers.CharField()
    id = serializers.CharField(help_text="Identificador del dispositivo")


class RondaActualSerializer(serializers.Serializer):
    """Estado de la ronda en curso."""

    partida = serializers.IntegerField()
    numero = serializers.IntegerField()
    total = serializers.IntegerField()
    puntos = serializers.IntegerField()
    hora = serializers.CharField()
    alertas = AlertaSerializer(many=True)


class DecisionSerializer(serializers.Serializer):
    """Alertas que el jugador decide atender."""

    alertas = serializers.ListField(
        child=serializers.IntegerField(min_value=1), allow_empty=True,
        help_text="Indices (desde 1) de las alertas atendidas; las demas se ignoran.",
    )


class ResultadoDecisionSerializer(serializers.Serializer):
    """Resultado de una decision."""

    ronda = RondaSerializer()
    partida = PartidaSerializer()


class EstadisticaSerializer(serializers.ModelSerializer):
    """Estadisticas de un jugador."""

    jugador = serializers.CharField(source="usuario.nombre_visible", read_only=True)
    derrotas = serializers.IntegerField(read_only=True)
    porcentaje_victorias = serializers.FloatField(read_only=True)
    promedio_puntos = serializers.FloatField(read_only=True)

    class Meta:
        model = Estadistica
        fields = ("jugador", "total_partidas", "victorias", "derrotas", "porcentaje_victorias",
                  "mejor_puntuacion", "promedio_puntos")
        read_only_fields = fields
