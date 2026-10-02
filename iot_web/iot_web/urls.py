"""Rutas principales del proyecto web."""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(("juego_app.api.urls", "api"))),
    path("", include("juego_app.urls")),
]
