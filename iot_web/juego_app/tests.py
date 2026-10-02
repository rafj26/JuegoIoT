"""Tests de la version web."""
from django.test import TestCase
from django.urls import reverse

from juego_app.adaptador import AdaptadorJuego, SeleccionInvalida
from juego_app.models import Estadistica, Partida, Usuario
from modelos.juego import JuegoSeguridadIoT


class BaseJuegoTest(TestCase):
    """Usuario con sesion iniciada."""

    def setUp(self):
        self.usuario = Usuario.objects.create_user("ana", password="clave-segura-123",
                                                   nombre_publico="Ana")
        self.client.force_login(self.usuario)

    def jugar_ronda(self, partida, seleccion):
        self.client.get(reverse("juego_app:ronda", args=[partida.pk]))
        return self.client.post(reverse("juego_app:decidir", args=[partida.pk]),
                                {"alertas": seleccion})


class AdaptadorTest(BaseJuegoTest):
    def test_alertas_persisten_entre_peticiones(self):
        partida = Partida.objects.create(usuario=self.usuario)
        AdaptadorJuego(partida).iniciar_ronda()
        partida.refresh_from_db()
        self.assertEqual(len(partida.alertas_pendientes), 8)

        primera = AdaptadorJuego(partida).get_alertas()
        segunda = AdaptadorJuego(partida).get_alertas()
        self.assertEqual(primera, segunda)
        self.assertNotIn("es_real", primera[0])

    def test_procesar_reutiliza_calculo_de_puntos(self):
        partida = Partida.objects.create(usuario=self.usuario)
        adaptador = AdaptadorJuego(partida)
        adaptador.iniciar_ronda()
        reales = [i for i, a in enumerate(partida.alertas_pendientes, 1) if a["es_real"]]

        ronda = adaptador.procesar(reales)
        partida.refresh_from_db()
        self.assertEqual(ronda.puntos, 2 * len(reales))
        self.assertEqual(partida.puntos, 15 + 2 * len(reales))
        self.assertEqual(partida.ronda_actual, 2)
        self.assertEqual(partida.alertas_pendientes, [])
        self.assertEqual(len(ronda.alertas_json), 8)

    def test_seleccion_invalida(self):
        partida = Partida.objects.create(usuario=self.usuario)
        adaptador = AdaptadorJuego(partida)
        with self.assertRaises(SeleccionInvalida):
            adaptador.procesar([1])
        adaptador.iniciar_ronda()
        with self.assertRaises(SeleccionInvalida):
            adaptador.procesar([9])


class FlujoJuegoTest(BaseJuegoTest):
    def test_paginas_publicas(self):
        self.client.logout()
        for nombre in ("home", "registro", "login", "leaderboard"):
            self.assertEqual(self.client.get(reverse(f"juego_app:{nombre}")).status_code, 200, nombre)

    def test_juego_requiere_login(self):
        self.client.logout()
        respuesta = self.client.post(reverse("juego_app:iniciar"))
        self.assertRedirects(respuesta, reverse("juego_app:login") + "?next=" + reverse("juego_app:iniciar"),
                             fetch_redirect_response=False)
        self.assertEqual(self.client.get(reverse("juego_app:perfil")).status_code, 302)

    def test_partida_completa(self):
        respuesta = self.client.post(reverse("juego_app:iniciar"))
        partida = Partida.objects.get(usuario=self.usuario)
        self.assertRedirects(respuesta, reverse("juego_app:ronda", args=[partida.pk]))

        pagina = self.client.get(reverse("juego_app:ronda", args=[partida.pk]))
        self.assertContains(pagina, "Confirmar decision")
        self.assertContains(pagina, 'name="alertas"', count=8)

        for numero in range(1, 6):
            respuesta = self.jugar_ronda(partida, [1, 2])
            self.assertRedirects(respuesta, reverse("juego_app:ronda_resultado", args=[partida.pk, numero]))
            self.assertContains(self.client.get(respuesta.url), f"Resultados de la ronda {numero}")

        partida.refresh_from_db()
        self.assertTrue(partida.terminada)
        self.assertEqual(partida.rondas.count(), 5)
        self.assertEqual(partida.victoria, partida.puntos >= JuegoSeguridadIoT.PUNTOS_VICTORIA)

        final = self.client.get(reverse("juego_app:resultado", args=[partida.pk]))
        self.assertContains(final, "VICTORIA" if partida.victoria else "DERROTA")
        self.assertContains(final, "<svg", html=False)

        estadistica = Estadistica.objects.get(usuario=self.usuario)
        self.assertEqual(estadistica.total_partidas, 1)
        self.assertEqual(estadistica.mejor_puntuacion, partida.puntos)

        # Una partida terminada no admite mas decisiones
        respuesta = self.client.post(reverse("juego_app:decidir", args=[partida.pk]), {"alertas": [1]})
        self.assertRedirects(respuesta, reverse("juego_app:resultado", args=[partida.pk]))
        self.assertEqual(partida.rondas.count(), 5)

    def test_recargar_ronda_no_cambia_alertas(self):
        partida = Partida.objects.create(usuario=self.usuario)
        url = reverse("juego_app:ronda", args=[partida.pk])
        self.client.get(url)
        partida.refresh_from_db()
        alertas = partida.alertas_pendientes
        self.client.get(url)
        partida.refresh_from_db()
        self.assertEqual(partida.alertas_pendientes, alertas)

    def test_no_revela_si_la_alerta_es_real(self):
        partida = Partida.objects.create(usuario=self.usuario)
        pagina = self.client.get(reverse("juego_app:ronda", args=[partida.pk]))
        self.assertNotContains(pagina, "es_real")
        self.assertNotContains(pagina, "REAL")

    def test_seleccion_fuera_de_rango(self):
        partida = Partida.objects.create(usuario=self.usuario)
        respuesta = self.jugar_ronda(partida, [99])
        self.assertRedirects(respuesta, reverse("juego_app:ronda", args=[partida.pk]))
        partida.refresh_from_db()
        self.assertEqual(partida.ronda_actual, 1)

    def test_no_puede_ver_partidas_ajenas(self):
        otro = Usuario.objects.create_user("luis", password="clave-segura-123")
        ajena = Partida.objects.create(usuario=otro)
        for nombre in ("ronda", "resultado"):
            self.assertEqual(self.client.get(reverse(f"juego_app:{nombre}", args=[ajena.pk])).status_code, 404)
        self.assertEqual(self.client.post(reverse("juego_app:decidir", args=[ajena.pk])).status_code, 404)


class CuentasTest(TestCase):
    def test_registro_inicia_sesion(self):
        respuesta = self.client.post(reverse("juego_app:registro"), {
            "username": "nuevo", "nombre_publico": "Nuevo", "email": "n@example.com",
            "password1": "una-clave-larga-9", "password2": "una-clave-larga-9",
        })
        self.assertRedirects(respuesta, reverse("juego_app:home"))
        self.assertTrue(Usuario.objects.filter(username="nuevo").exists())
        self.assertContains(self.client.get(reverse("juego_app:perfil")), "Nuevo")

    def test_login_y_logout(self):
        Usuario.objects.create_user("ana", password="clave-segura-123")
        respuesta = self.client.post(reverse("juego_app:login"),
                                     {"username": "ana", "password": "clave-segura-123"})
        self.assertRedirects(respuesta, reverse("juego_app:home"))
        self.client.post(reverse("juego_app:logout"))
        self.assertEqual(self.client.get(reverse("juego_app:perfil")).status_code, 302)


class EstadisticasTest(BaseJuegoTest):
    def test_registrar_partidas(self):
        for puntos, victoria in [(20, True), (10, False)]:
            partida = Partida.objects.create(usuario=self.usuario, puntos=puntos,
                                             victoria=victoria, terminada=True)
            Estadistica.registrar_partida(partida)
        e = Estadistica.objects.get(usuario=self.usuario)
        self.assertEqual((e.total_partidas, e.victorias, e.derrotas), (2, 1, 1))
        self.assertEqual(e.mejor_puntuacion, 20)
        self.assertEqual(e.porcentaje_victorias, 50.0)
        self.assertEqual(e.promedio_puntos, 15.0)

    def test_leaderboard_y_perfil(self):
        partida = Partida.objects.create(usuario=self.usuario, puntos=21, victoria=True, terminada=True)
        Estadistica.registrar_partida(partida)
        self.assertContains(self.client.get(reverse("juego_app:leaderboard")), "Ana")
        perfil = self.client.get(reverse("juego_app:perfil"))
        self.assertContains(perfil, "21")
        respuesta = self.client.post(reverse("juego_app:perfil"),
                                     {"nombre_publico": "Ana B", "email": "ana@example.com"})
        self.assertRedirects(respuesta, reverse("juego_app:perfil"))
        self.usuario.refresh_from_db()
        self.assertEqual(self.usuario.nombre_publico, "Ana B")

    def test_admin_registrado(self):
        Usuario.objects.create_superuser("admin", "a@example.com", "clave-segura-123")
        self.client.login(username="admin", password="clave-segura-123")
        for modelo in ("usuario", "partida", "ronda", "estadistica"):
            url = reverse(f"admin:juego_app_{modelo}_changelist")
            self.assertEqual(self.client.get(url).status_code, 200, modelo)
