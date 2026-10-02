"""Rutas de la aplicacion del juego."""
from django.contrib.auth.views import LogoutView
from django.urls import path

from juego_app import views

app_name = "juego_app"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("registro/", views.RegistroView.as_view(), name="registro"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("jugar/", views.IniciarJuegoView.as_view(), name="iniciar"),
    path("partida/<int:pk>/", views.RondaView.as_view(), name="ronda"),
    path("partida/<int:pk>/decidir/", views.DecidirView.as_view(), name="decidir"),
    path("partida/<int:pk>/ronda/<int:numero>/", views.RondaResultadoView.as_view(),
         name="ronda_resultado"),
    path("partida/<int:pk>/resultado/", views.ResultadoView.as_view(), name="resultado"),
    path("clasificacion/", views.LeaderboardView.as_view(), name="leaderboard"),
    path("perfil/", views.PerfilView.as_view(), name="perfil"),
]
