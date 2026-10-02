"""Vistas (controladores web) del juego."""
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView as BaseLoginView
from django.db import transaction
from django.db.models import Max
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import CreateView, DetailView, ListView, TemplateView

from juego_app.adaptador import AdaptadorJuego, SeleccionInvalida
from juego_app.forms import DecisionForm, LoginForm, PerfilForm, RegistroForm
from juego_app.models import Estadistica, Partida
from modelos.juego import JuegoSeguridadIoT


class HomeView(TemplateView):
    """Pagina principal con reglas y acceso al juego."""

    template_name = "juego_app/home.html"

    def get_context_data(self, **kwargs):
        """Agrega reglas, partida en curso y mejores jugadores."""
        contexto = super().get_context_data(**kwargs)
        contexto["info"] = JuegoSeguridadIoT.get_info_inicial()
        contexto["top"] = (Estadistica.objects.filter(total_partidas__gt=0)
                           .select_related("usuario")[:5])
        if self.request.user.is_authenticated:
            contexto["partida_en_curso"] = (self.request.user.partidas
                                            .filter(terminada=False).first())
        return contexto


class RegistroView(CreateView):
    """Registro de usuario; inicia sesion al terminar."""

    form_class = RegistroForm
    template_name = "juego_app/registro.html"
    success_url = reverse_lazy("juego_app:home")

    def dispatch(self, request, *args, **kwargs):
        """Redirige a la portada si el usuario ya inicio sesion."""
        if request.user.is_authenticated:
            return redirect("juego_app:home")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """Crea el usuario e inicia su sesion."""
        respuesta = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request, f"Bienvenido, {self.object.nombre_visible}")
        return respuesta


class LoginView(BaseLoginView):
    """Inicio de sesion."""

    template_name = "juego_app/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True


class IniciarJuegoView(LoginRequiredMixin, View):
    """Crea una partida nueva (solo POST)."""

    def post(self, request):
        """Crea la partida y redirige a la primera ronda."""
        partida = Partida.objects.create(usuario=request.user)
        return redirect("juego_app:ronda", pk=partida.pk)


class PartidaUsuarioMixin(LoginRequiredMixin):
    """Obtiene una partida que pertenezca al usuario actual."""

    def get_partida(self, pk, bloquear=False):
        """Devuelve la partida o 404 si no es del usuario."""
        consulta = Partida.objects.filter(usuario=self.request.user)
        if bloquear:
            consulta = consulta.select_for_update()
        return get_object_or_404(consulta, pk=pk)


class RondaView(PartidaUsuarioMixin, TemplateView):
    """Muestra las alertas de la ronda en curso."""

    template_name = "juego_app/juego.html"

    def get(self, request, pk):
        """Genera (si hace falta) y muestra las alertas."""
        with transaction.atomic():
            partida = self.get_partida(pk, bloquear=True)
            if partida.terminada:
                return redirect("juego_app:resultado", pk=partida.pk)
            adaptador = AdaptadorJuego(partida)
            hora = adaptador.iniciar_ronda()

        alertas = adaptador.get_alertas()
        contexto = self.get_context_data(
            partida=partida,
            info=adaptador.get_info_ronda(),
            hora=hora,
            alertas=alertas,
            historial=self._historial(partida),
            puntos_victoria=JuegoSeguridadIoT.PUNTOS_VICTORIA,
            form=DecisionForm(total_alertas=len(alertas)),
        )
        return self.render_to_response(contexto)

    @staticmethod
    def _historial(partida):
        """Puntos al inicio y despues de cada ronda."""
        return [JuegoSeguridadIoT.PUNTOS_INICIALES] + [r.puntos_acumulados for r in partida.rondas.all()]


class DecidirView(PartidaUsuarioMixin, View):
    """Procesa las alertas que el jugador decide atender (solo POST)."""

    def post(self, request, pk):
        """Valida la seleccion, calcula puntos y redirige al resultado de la ronda."""
        with transaction.atomic():
            partida = self.get_partida(pk, bloquear=True)
            if partida.terminada:
                return redirect("juego_app:resultado", pk=partida.pk)
            adaptador = AdaptadorJuego(partida)
            form = DecisionForm(request.POST, total_alertas=len(partida.alertas_pendientes))
            if not form.is_valid():
                messages.error(request, "Seleccion invalida, revisa las alertas marcadas.")
                return redirect("juego_app:ronda", pk=partida.pk)
            try:
                ronda = adaptador.procesar(form.cleaned_data["alertas"])
            except SeleccionInvalida as error:
                messages.error(request, str(error))
                return redirect("juego_app:ronda", pk=partida.pk)

        return redirect("juego_app:ronda_resultado", pk=partida.pk, numero=ronda.numero)


class RondaResultadoView(PartidaUsuarioMixin, TemplateView):
    """Resultado de una ronda ya jugada."""

    template_name = "juego_app/ronda_resultado.html"

    def get_context_data(self, **kwargs):
        """Agrega la ronda, la partida y el resumen de aciertos."""
        contexto = super().get_context_data(**kwargs)
        partida = self.get_partida(kwargs["pk"])
        ronda = get_object_or_404(partida.rondas, numero=kwargs["numero"])
        aciertos = sum(1 for a in ronda.alertas_json if a["atendida"] == a["es_real"])
        contexto.update(
            partida=partida,
            ronda=ronda,
            aciertos=aciertos,
            total_rondas=JuegoSeguridadIoT.TOTAL_RONDAS,
            puntos_victoria=JuegoSeguridadIoT.PUNTOS_VICTORIA,
            siguiente=(reverse("juego_app:resultado", args=[partida.pk]) if partida.terminada
                       else reverse("juego_app:ronda", args=[partida.pk])),
        )
        return contexto


class ResultadoView(PartidaUsuarioMixin, DetailView):
    """Resultado final de una partida."""

    template_name = "juego_app/resultado.html"
    context_object_name = "partida"

    def get_queryset(self):
        """Solo partidas terminadas del usuario."""
        return Partida.objects.filter(usuario=self.request.user, terminada=True)

    def get(self, request, *args, **kwargs):
        """Si la partida no termino, vuelve a la ronda en curso."""
        partida = self.get_partida(kwargs["pk"])
        if not partida.terminada:
            return redirect("juego_app:ronda", pk=partida.pk)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Agrega rondas, historial de puntos y objetivo."""
        contexto = super().get_context_data(**kwargs)
        rondas = list(self.object.rondas.all())
        contexto.update(
            rondas=rondas,
            historial=[JuegoSeguridadIoT.PUNTOS_INICIALES] + [r.puntos_acumulados for r in rondas],
            puntos_victoria=JuegoSeguridadIoT.PUNTOS_VICTORIA,
            mensaje=JuegoSeguridadIoT.get_mensaje_final(self.object.victoria),
        )
        return contexto


class LeaderboardView(ListView):
    """Tabla de clasificacion global."""

    template_name = "juego_app/leaderboard.html"
    context_object_name = "estadisticas"

    def get_queryset(self):
        """Jugadores con al menos una partida, por victorias y mejor puntuacion."""
        return (Estadistica.objects.filter(total_partidas__gt=0)
                .select_related("usuario")[:50])

    def get_context_data(self, **kwargs):
        """Agrega las mejores partidas individuales."""
        contexto = super().get_context_data(**kwargs)
        contexto["mejores_partidas"] = (Partida.objects.filter(terminada=True)
                                        .select_related("usuario")
                                        .order_by("-puntos", "fecha")[:10])
        return contexto


class PerfilView(LoginRequiredMixin, TemplateView):
    """Perfil del usuario: datos, estadisticas e historial."""

    template_name = "juego_app/perfil.html"

    def get_context_data(self, **kwargs):
        """Agrega estadisticas, historial y formulario de perfil."""
        contexto = super().get_context_data(**kwargs)
        usuario = self.request.user
        partidas = usuario.partidas.all()
        contexto.update(
            estadistica=Estadistica.objects.filter(usuario=usuario).first(),
            partidas=partidas[:30],
            mejor=partidas.filter(terminada=True).aggregate(mejor=Max("puntos"))["mejor"],
            form=kwargs.get("form") or PerfilForm(instance=usuario),
        )
        return contexto

    def post(self, request):
        """Guarda los cambios del perfil."""
        form = PerfilForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil actualizado")
            return redirect("juego_app:perfil")
        return self.render_to_response(self.get_context_data(form=form))
