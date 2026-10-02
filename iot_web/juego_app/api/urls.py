"""Rutas de la API REST."""
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter

from juego_app.api import views

router = DefaultRouter()
router.register("partidas", views.PartidaViewSet, basename="partida")
router.register("rondas", views.RondaViewSet, basename="ronda")

urlpatterns = [
    path("", include(router.urls)),
    path("leaderboard/", views.LeaderboardView.as_view(), name="leaderboard"),
    path("estadisticas/", views.EstadisticasView.as_view(), name="estadisticas"),
    path("token/", obtain_auth_token, name="token"),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="api:schema"), name="swagger"),
    path("redoc/", SpectacularRedocView.as_view(url_name="api:schema"), name="redoc"),
]
