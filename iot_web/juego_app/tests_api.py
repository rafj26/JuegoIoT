"""Tests de la API REST."""
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from juego_app.models import Estadistica, Partida, Usuario


class BaseAPITest(APITestCase):
    """Cliente autenticado con token."""

    def setUp(self):
        self.usuario = Usuario.objects.create_user("ana", password="clave-segura-123",
                                                   nombre_publico="Ana")
        token = Token.objects.create(user=self.usuario)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    def crear_partida(self):
        respuesta = self.client.post(reverse("api:partida-list"))
        self.assertEqual(respuesta.status_code, 201)
        return respuesta.data["id"]


class AutenticacionTest(APITestCase):
    def test_obtener_token(self):
        Usuario.objects.create_user("ana", password="clave-segura-123")
        respuesta = self.client.post(reverse("api:token"),
                                     {"username": "ana", "password": "clave-segura-123"})
        self.assertEqual(respuesta.status_code, 200)
        self.assertIn("token", respuesta.data)

    def test_requiere_autenticacion(self):
        for url in (reverse("api:partida-list"), reverse("api:ronda-list"), reverse("api:estadisticas")):
            self.assertEqual(self.client.get(url).status_code, 401, url)

    def test_leaderboard_publico(self):
        self.assertEqual(self.client.get(reverse("api:leaderboard")).status_code, 200)

    def test_documentacion(self):
        self.assertEqual(self.client.get(reverse("api:schema")).status_code, 200)
        self.assertEqual(self.client.get(reverse("api:swagger")).status_code, 200)
        self.assertEqual(self.client.get(reverse("api:redoc")).status_code, 200)


class PartidasAPITest(BaseAPITest):
    def test_partida_completa(self):
        partida_id = self.crear_partida()
        for numero in range(1, 6):
            ronda = self.client.get(reverse("api:partida-ronda", args=[partida_id]))
            self.assertEqual(ronda.status_code, 200)
            self.assertEqual(ronda.data["numero"], numero)
            self.assertEqual(len(ronda.data["alertas"]), 8)
            self.assertNotIn("es_real", ronda.data["alertas"][0])

            resultado = self.client.post(reverse("api:partida-decidir", args=[partida_id]),
                                         {"alertas": [1, 2]}, format="json")
            self.assertEqual(resultado.status_code, 200, resultado.data)
            self.assertEqual(resultado.data["ronda"]["numero"], numero)
            self.assertIn("es_real", resultado.data["ronda"]["alertas"][0])

        detalle = self.client.get(reverse("api:partida-detail", args=[partida_id]))
        self.assertTrue(detalle.data["terminada"])
        self.assertEqual(len(detalle.data["rondas"]), 5)

        rondas = self.client.get(reverse("api:ronda-list"), {"partida": partida_id})
        self.assertEqual(rondas.data["count"], 5)

        stats = self.client.get(reverse("api:estadisticas"))
        self.assertEqual(stats.data["total_partidas"], 1)
        self.assertEqual(stats.data["mejor_puntuacion"], detalle.data["puntos"])

        leaderboard = self.client.get(reverse("api:leaderboard"))
        self.assertEqual(leaderboard.data["results"][0]["jugador"], "Ana")

        terminada = self.client.get(reverse("api:partida-ronda", args=[partida_id]))
        self.assertEqual(terminada.status_code, 400)

    def test_decidir_sin_ronda_o_invalida(self):
        partida_id = self.crear_partida()
        url = reverse("api:partida-decidir", args=[partida_id])
        self.assertEqual(self.client.post(url, {"alertas": [1]}, format="json").status_code, 400)
        self.client.get(reverse("api:partida-ronda", args=[partida_id]))
        self.assertEqual(self.client.post(url, {"alertas": [9]}, format="json").status_code, 400)
        self.assertEqual(self.client.post(url, {"alertas": ["x"]}, format="json").status_code, 400)
        self.assertEqual(self.client.post(url, {"alertas": []}, format="json").status_code, 200)

    def test_no_se_pueden_editar_puntos(self):
        partida_id = self.crear_partida()
        url = reverse("api:partida-detail", args=[partida_id])
        self.assertEqual(self.client.patch(url, {"puntos": 999}, format="json").status_code, 405)
        self.assertEqual(Partida.objects.get(pk=partida_id).puntos, 15)

    def test_eliminar_solo_en_curso(self):
        partida_id = self.crear_partida()
        self.assertEqual(self.client.delete(reverse("api:partida-detail", args=[partida_id])).status_code, 204)
        terminada = Partida.objects.create(usuario=self.usuario, terminada=True)
        self.assertEqual(self.client.delete(reverse("api:partida-detail", args=[terminada.pk])).status_code, 400)

    def test_aislamiento_entre_usuarios(self):
        otro = Usuario.objects.create_user("luis", password="clave-segura-123")
        ajena = Partida.objects.create(usuario=otro)
        self.assertEqual(self.client.get(reverse("api:partida-detail", args=[ajena.pk])).status_code, 404)
        self.assertEqual(self.client.get(reverse("api:partida-ronda", args=[ajena.pk])).status_code, 404)
        self.assertEqual(self.client.get(reverse("api:partida-list")).data["count"], 0)

    def test_filtro_partida_invalido(self):
        self.assertEqual(self.client.get(reverse("api:ronda-list"), {"partida": "x"}).status_code, 400)

    def test_estadisticas_vacias(self):
        datos = self.client.get(reverse("api:estadisticas")).data
        self.assertEqual(datos["total_partidas"], 0)
        self.assertEqual(datos["porcentaje_victorias"], 0.0)
        self.assertTrue(Estadistica.objects.filter(usuario=self.usuario).exists())
