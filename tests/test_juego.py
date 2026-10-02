import pytest

from modelos.juego import JuegoSeguridadIoT


class TestCalcularPuntos:
    @pytest.mark.parametrize("es_real, atendida, esperado", [
        (True, True, JuegoSeguridadIoT.PUNTOS_ALERTA_REAL_ATENDIDA),
        (False, True, JuegoSeguridadIoT.PUNTOS_ALERTA_FALSA_ATENDIDA),
        (True, False, JuegoSeguridadIoT.PUNTOS_ALERTA_REAL_NO_ATENDIDA),
        (False, False, JuegoSeguridadIoT.PUNTOS_ALERTA_FALSA_NO_ATENDIDA),
    ])
    def test_cambio_segun_reglas(self, juego, crear_alerta, es_real, atendida, esperado):
        assert juego._calcular_cambio_puntos(crear_alerta(es_real), atendida) == esperado

    def test_valores_de_las_reglas(self):
        assert JuegoSeguridadIoT.PUNTOS_ALERTA_REAL_ATENDIDA == 2
        assert JuegoSeguridadIoT.PUNTOS_ALERTA_FALSA_ATENDIDA == -1
        assert JuegoSeguridadIoT.PUNTOS_ALERTA_REAL_NO_ATENDIDA == -2
        assert JuegoSeguridadIoT.PUNTOS_ALERTA_FALSA_NO_ATENDIDA == 0

    @pytest.mark.parametrize("es_real, atendida, texto", [
        (True, True, "Correcto - Alerta real atendida"),
        (False, True, "Falsa alarma atendida"),
        (True, False, "Error - Alerta real ignorada"),
        (False, False, "Correcto - Falsa alarma ignorada"),
    ])
    def test_descripcion_resultado(self, juego, crear_alerta, es_real, atendida, texto):
        assert juego._get_descripcion_resultado(crear_alerta(es_real), atendida) == texto


class TestProcesarDecisiones:
    def test_atender_solo_reales(self, juego_controlado):
        juego_controlado.iniciar_ronda()
        resultados = juego_controlado.procesar_decisiones([1, 3])
        assert [r['cambio_puntos'] for r in resultados] == [2, 0, 2, 0]
        assert juego_controlado.puntos == 15 + 4

    def test_atender_todas(self, juego_controlado):
        juego_controlado.iniciar_ronda()
        juego_controlado.procesar_decisiones([1, 2, 3, 4])
        assert juego_controlado.puntos == 15 + 2 - 1 + 2 - 1

    def test_no_atender_ninguna(self, juego_controlado):
        juego_controlado.iniciar_ronda()
        resultados = juego_controlado.procesar_decisiones([])
        assert all(not r['atendida'] for r in resultados)
        assert juego_controlado.puntos == 15 - 4

    def test_estructura_resultado(self, juego_controlado):
        juego_controlado.iniciar_ronda()
        resultado = juego_controlado.procesar_decisiones([1])[0]
        assert set(resultado) == {'indice', 'atendida', 'es_real', 'cambio_puntos', 'descripcion'}
        assert resultado['indice'] == 1 and resultado['atendida'] and resultado['es_real']

    def test_registra_historial_de_ronda(self, juego_controlado):
        juego_controlado.iniciar_ronda()
        juego_controlado.procesar_decisiones([1])
        ronda = juego_controlado.historial_rondas[0]
        assert ronda['numero'] == 1
        assert ronda['hora'] == "08:00"
        assert ronda['puntos_ronda'] == 2 - 2
        assert ronda['puntos_acumulados'] == juego_controlado.puntos
        assert len(ronda['alertas']) == 4
        assert ronda['alertas'][0]['atendida'] is True


class TestValidarSeleccion:
    def test_seleccion_vacia_es_valida(self, juego_controlado):
        juego_controlado.iniciar_ronda()
        assert juego_controlado.validar_seleccion([])

    def test_seleccion_en_rango(self, juego_controlado):
        juego_controlado.iniciar_ronda()
        assert juego_controlado.validar_seleccion([1, 2, 3, 4])

    @pytest.mark.parametrize("seleccion", [[0], [5], [1, 99], [-1]])
    def test_seleccion_fuera_de_rango(self, juego_controlado, seleccion):
        juego_controlado.iniciar_ronda()
        assert not juego_controlado.validar_seleccion(seleccion)


class TestRondas:
    def test_estado_inicial(self, juego):
        assert juego.puntos == JuegoSeguridadIoT.PUNTOS_INICIALES
        assert juego.ronda_actual == 1
        assert juego.tiene_rondas_pendientes()

    def test_avanzar_ronda(self, juego):
        juego.avanzar_ronda()
        assert juego.ronda_actual == 2
        assert juego.get_info_ronda() == {'numero': 2, 'total': 5, 'puntos': 15}

    def test_sin_rondas_tras_la_ultima(self, juego):
        for _ in range(JuegoSeguridadIoT.TOTAL_RONDAS):
            assert juego.tiene_rondas_pendientes()
            juego.avanzar_ronda()
        assert not juego.tiene_rondas_pendientes()

    def test_hora_avanza_tres_horas_por_ronda(self, juego):
        horas = []
        for _ in range(JuegoSeguridadIoT.TOTAL_RONDAS):
            horas.append(juego.iniciar_ronda().strftime("%H:%M"))
            juego.avanzar_ronda()
        assert horas == ["08:00", "11:00", "14:00", "17:00", "20:00"]

    def test_iniciar_ronda_genera_alertas(self, juego):
        juego.iniciar_ronda()
        assert len(juego.alertas_actuales) == 8
        formateadas = juego.get_alertas_formateadas()
        assert [a['indice'] for a in formateadas] == list(range(1, 9))


class TestInfoYResultado:
    def test_info_inicial(self, juego):
        info = juego.get_info_inicial()
        assert info['puntos_iniciales'] == 15
        assert info['total_rondas'] == 5
        assert info['puntos_victoria'] == 15
        assert info['reglas']['alerta_real_atendida'] == 2

    @pytest.mark.parametrize("puntos, victoria", [(15, True), (30, True), (14, False), (-3, False)])
    def test_resultado_final(self, juego, puntos, victoria):
        juego.puntos = puntos
        resultado = juego.get_resultado_final()
        assert resultado['puntos_finales'] == puntos
        assert resultado['victoria'] is victoria
        assert resultado['mensaje']
