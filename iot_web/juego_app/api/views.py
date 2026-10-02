"""Vistas de la API REST."""
from django.db import transaction
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import generics, mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from juego_app.adaptador import AdaptadorJuego, SeleccionInvalida
from juego_app.api.serializers import (DecisionSerializer, EstadisticaSerializer,
                                       PartidaDetalleSerializer, PartidaSerializer,
                                       ResultadoDecisionSerializer, RondaActualSerializer,
                                       RondaSerializer)
from juego_app.models import Estadistica, Partida, Ronda


@extend_schema_view(
    list=extend_schema(summary="Listar mis partidas"),
    retrieve=extend_schema(summary="Ver una partida con sus rondas"),
    create=extend_schema(summary="Crear una partida nueva", request=None),
    destroy=extend_schema(summary="Eliminar una partida en curso"),
)
class PartidaViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin,
                     mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """
    CRUD de partidas del usuario autenticado.

    Las partidas se juegan (se modifican) con las acciones ``ronda`` y
    ``decidir``; los puntos no se pueden editar directamente.
    """

    def get_queryset(self):
        """Solo las partidas del usuario."""
        if getattr(self, "swagger_fake_view", False):  # generacion del esquema OpenAPI
            return Partida.objects.none()
        return Partida.objects.filter(usuario=self.request.user).prefetch_related("rondas")

    def get_serializer_class(self):
        """Detalle con rondas en ``retrieve``."""
        if self.action == "retrieve":
            return PartidaDetalleSerializer
        return PartidaSerializer

    def perform_create(self, serializer):
        """Asigna la partida al usuario autenticado."""
        serializer.save(usuario=self.request.user)

    def perform_destroy(self, instance):
        """Solo se eliminan partidas en curso para no alterar estadisticas."""
        if instance.terminada:
            raise ValidationError("No se puede eliminar una partida terminada.")
        instance.delete()

    @extend_schema(summary="Obtener la ronda en curso", request=None,
                   responses=RondaActualSerializer)
    @action(detail=True, methods=["get"])
    def ronda(self, request, pk=None):
        """Devuelve las alertas de la ronda actual (las genera si hace falta)."""
        with transaction.atomic():
            partida = self.get_queryset().select_for_update().get(pk=self.get_object().pk)
            if partida.terminada:
                raise ValidationError("La partida ya termino.")
            adaptador = AdaptadorJuego(partida)
            hora = adaptador.iniciar_ronda()

        info = adaptador.get_info_ronda()
        datos = {"partida": partida.pk, "hora": hora.strftime("%H:%M"),
                 "alertas": adaptador.get_alertas(), **info}
        return Response(RondaActualSerializer(datos).data)

    @extend_schema(summary="Decidir que alertas atender", request=DecisionSerializer,
                   responses={200: ResultadoDecisionSerializer})
    @action(detail=True, methods=["post"])
    def decidir(self, request, pk=None):
        """Procesa la decision de la ronda en curso y devuelve el resultado."""
        entrada = DecisionSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)

        with transaction.atomic():
            partida = self.get_queryset().select_for_update().get(pk=self.get_object().pk)
            if partida.terminada:
                raise ValidationError("La partida ya termino.")
            if not partida.alertas_pendientes:
                raise ValidationError("Primero obten la ronda en curso (GET .../ronda/).")
            try:
                ronda = AdaptadorJuego(partida).procesar(entrada.validated_data["alertas"])
            except SeleccionInvalida as error:
                raise ValidationError(str(error))

        datos = {"ronda": RondaSerializer(ronda).data, "partida": PartidaSerializer(partida).data}
        return Response(datos, status=status.HTTP_200_OK)


@extend_schema_view(
    list=extend_schema(summary="Listar mis rondas", parameters=[
        OpenApiParameter("partida", int, description="Filtra por id de partida")]),
    retrieve=extend_schema(summary="Ver una ronda"),
)
class RondaViewSet(viewsets.ReadOnlyModelViewSet):
    """Rondas jugadas por el usuario autenticado."""

    serializer_class = RondaSerializer

    def get_queryset(self):
        """Rondas del usuario, opcionalmente de una partida."""
        if getattr(self, "swagger_fake_view", False):  # generacion del esquema OpenAPI
            return Ronda.objects.none()
        consulta = Ronda.objects.filter(partida__usuario=self.request.user)
        partida = self.request.query_params.get("partida")
        if partida is not None:
            if not partida.isdigit():
                raise ValidationError({"partida": "Debe ser un numero."})
            consulta = consulta.filter(partida_id=int(partida))
        return consulta


@extend_schema(summary="Tabla de clasificacion")
class LeaderboardView(generics.ListAPIView):
    """Clasificacion global, por victorias y mejor puntuacion (publica)."""

    serializer_class = EstadisticaSerializer
    permission_classes = [permissions.AllowAny]
    queryset = Estadistica.objects.filter(total_partidas__gt=0).select_related("usuario")


@extend_schema(summary="Mis estadisticas")
class EstadisticasView(generics.RetrieveAPIView):
    """Estadisticas del usuario autenticado."""

    serializer_class = EstadisticaSerializer

    def get_object(self):
        """Estadisticas del usuario (vacias si aun no termino partidas)."""
        estadistica, _ = Estadistica.objects.get_or_create(usuario=self.request.user)
        return estadistica
