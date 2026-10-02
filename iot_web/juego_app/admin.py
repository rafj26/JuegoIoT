"""Configuracion del panel de administracion."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from juego_app.models import Estadistica, Partida, Ronda, Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    """Administracion de usuarios con el campo nombre_publico."""

    fieldsets = UserAdmin.fieldsets + (("Juego", {"fields": ("nombre_publico",)}),)
    list_display = ("username", "nombre_publico", "email", "is_staff", "date_joined")


class RondaInline(admin.TabularInline):
    """Rondas dentro de la ficha de una partida."""

    model = Ronda
    extra = 0
    fields = ("numero", "hora", "puntos", "puntos_acumulados")
    readonly_fields = fields
    can_delete = False


@admin.register(Partida)
class PartidaAdmin(admin.ModelAdmin):
    """Administracion de partidas."""

    list_display = ("id", "usuario", "fecha", "puntos", "victoria", "terminada", "ronda_actual")
    list_filter = ("terminada", "victoria", "fecha")
    search_fields = ("usuario__username", "usuario__nombre_publico")
    date_hierarchy = "fecha"
    inlines = [RondaInline]


@admin.register(Ronda)
class RondaAdmin(admin.ModelAdmin):
    """Administracion de rondas."""

    list_display = ("partida", "numero", "hora", "puntos", "puntos_acumulados")
    list_filter = ("numero",)


@admin.register(Estadistica)
class EstadisticaAdmin(admin.ModelAdmin):
    """Administracion de estadisticas."""

    list_display = ("usuario", "total_partidas", "victorias", "mejor_puntuacion", "puntos_totales")
    search_fields = ("usuario__username",)
