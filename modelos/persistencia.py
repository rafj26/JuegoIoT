"""Persistencia de partidas en una base de datos SQLite."""
import csv
import json
import logging
import os
import sqlite3
from datetime import datetime

logger = logging.getLogger(__name__)

RUTA_BD_POR_DEFECTO = os.path.join("datos", "partidas.db")

ESQUEMA = """
CREATE TABLE IF NOT EXISTS partidas (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    jugador         TEXT    NOT NULL,
    fecha           TEXT    NOT NULL,
    puntos_finales  INTEGER NOT NULL,
    victoria        INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS rondas (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    partida_id         INTEGER NOT NULL REFERENCES partidas(id) ON DELETE CASCADE,
    numero             INTEGER NOT NULL,
    hora               TEXT    NOT NULL,
    puntos_ronda       INTEGER NOT NULL,
    puntos_acumulados  INTEGER NOT NULL,
    alertas_json       TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS estadisticas (
    jugador           TEXT    PRIMARY KEY,
    total_partidas    INTEGER NOT NULL DEFAULT 0,
    victorias         INTEGER NOT NULL DEFAULT 0,
    mejor_puntuacion  INTEGER NOT NULL,
    puntos_totales    INTEGER NOT NULL DEFAULT 0
);
"""


class RepositorioPartidas:
    """
    Guarda y consulta partidas, rondas y estadisticas en SQLite.

    Args:
        ruta (str): Ruta del archivo de base de datos. Se usa ``":memory:"``
            para una base temporal en memoria.
    """

    def __init__(self, ruta=RUTA_BD_POR_DEFECTO):
        self.ruta = ruta
        carpeta = os.path.dirname(ruta)
        if ruta != ":memory:" and carpeta:
            os.makedirs(carpeta, exist_ok=True)
        self._conexion = sqlite3.connect(ruta)
        self._conexion.row_factory = sqlite3.Row
        self._conexion.execute("PRAGMA foreign_keys = ON")
        self._conexion.executescript(ESQUEMA)

    def cerrar(self):
        """Cierra la conexion con la base de datos."""
        self._conexion.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.cerrar()

    def guardar_partida(self, juego, jugador="Jugador", fecha=None):
        """
        Guarda una partida terminada con todas sus rondas.

        Tambien actualiza la tabla de estadisticas del jugador.

        Args:
            juego (JuegoSeguridadIoT): Partida ya jugada.
            jugador (str): Nombre del jugador.
            fecha (datetime, optional): Fecha de la partida. Por defecto, ahora.

        Returns:
            int: Identificador de la partida guardada.
        """
        fecha = (fecha or datetime.now()).isoformat(timespec="seconds")
        victoria = juego.puntos >= juego.PUNTOS_VICTORIA

        with self._conexion:
            cursor = self._conexion.execute(
                "INSERT INTO partidas (jugador, fecha, puntos_finales, victoria) "
                "VALUES (?, ?, ?, ?)",
                (jugador, fecha, juego.puntos, int(victoria)),
            )
            partida_id = cursor.lastrowid

            self._conexion.executemany(
                "INSERT INTO rondas (partida_id, numero, hora, puntos_ronda, "
                "puntos_acumulados, alertas_json) VALUES (?, ?, ?, ?, ?, ?)",
                [
                    (partida_id, r['numero'], r['hora'], r['puntos_ronda'],
                     r['puntos_acumulados'], json.dumps(r['alertas'], ensure_ascii=False))
                    for r in juego.historial_rondas
                ],
            )

            self._conexion.execute(
                "INSERT INTO estadisticas "
                "(jugador, total_partidas, victorias, mejor_puntuacion, puntos_totales) "
                "VALUES (?, 1, ?, ?, ?) "
                "ON CONFLICT(jugador) DO UPDATE SET "
                "total_partidas = total_partidas + 1, "
                "victorias = victorias + excluded.victorias, "
                "mejor_puntuacion = MAX(mejor_puntuacion, excluded.mejor_puntuacion), "
                "puntos_totales = puntos_totales + excluded.puntos_totales",
                (jugador, int(victoria), juego.puntos, juego.puntos),
            )

        logger.info("Partida %d guardada para %s (%d puntos)",
                    partida_id, jugador, juego.puntos)
        return partida_id

    def ver_historial(self, jugador=None, limite=None):
        """
        Lista las partidas guardadas, de la mas reciente a la mas antigua.

        Args:
            jugador (str, optional): Filtra por jugador.
            limite (int, optional): Numero maximo de partidas.

        Returns:
            list[dict]: Partidas con ``id``, ``jugador``, ``fecha``,
            ``puntos_finales`` y ``victoria``.
        """
        consulta = "SELECT id, jugador, fecha, puntos_finales, victoria FROM partidas"
        parametros = []
        if jugador is not None:
            consulta += " WHERE jugador = ?"
            parametros.append(jugador)
        consulta += " ORDER BY fecha DESC, id DESC"
        if limite is not None:
            consulta += " LIMIT ?"
            parametros.append(limite)

        filas = self._conexion.execute(consulta, parametros).fetchall()
        return [self._fila_partida(fila) for fila in filas]

    def ver_rondas(self, partida_id):
        """
        Devuelve las rondas de una partida, con sus alertas decodificadas.

        Args:
            partida_id (int): Identificador de la partida.

        Returns:
            list[dict]: Rondas ordenadas por numero.
        """
        filas = self._conexion.execute(
            "SELECT numero, hora, puntos_ronda, puntos_acumulados, alertas_json "
            "FROM rondas WHERE partida_id = ? ORDER BY numero",
            (partida_id,),
        ).fetchall()
        return [
            {
                'numero': fila['numero'],
                'hora': fila['hora'],
                'puntos_ronda': fila['puntos_ronda'],
                'puntos_acumulados': fila['puntos_acumulados'],
                'alertas': json.loads(fila['alertas_json']),
            }
            for fila in filas
        ]

    def ver_estadisticas(self, jugador=None):
        """
        Devuelve las estadisticas acumuladas por jugador.

        Args:
            jugador (str, optional): Si se indica, solo ese jugador.

        Returns:
            list[dict]: Estadisticas con porcentaje de victorias y promedio
            de puntos, ordenadas por victorias.
        """
        consulta = ("SELECT jugador, total_partidas, victorias, mejor_puntuacion, "
                    "puntos_totales FROM estadisticas")
        parametros = []
        if jugador is not None:
            consulta += " WHERE jugador = ?"
            parametros.append(jugador)
        consulta += " ORDER BY victorias DESC, mejor_puntuacion DESC"

        resultado = []
        for fila in self._conexion.execute(consulta, parametros).fetchall():
            total = fila['total_partidas']
            resultado.append({
                'jugador': fila['jugador'],
                'total_partidas': total,
                'victorias': fila['victorias'],
                'derrotas': total - fila['victorias'],
                'porcentaje_victorias': round(100 * fila['victorias'] / total, 1) if total else 0.0,
                'mejor_puntuacion': fila['mejor_puntuacion'],
                'promedio_puntos': round(fila['puntos_totales'] / total, 1) if total else 0.0,
            })
        return resultado

    def exportar_csv(self, ruta, jugador=None):
        """
        Exporta el historial de partidas a un archivo CSV.

        Args:
            ruta (str): Ruta del archivo CSV de salida.
            jugador (str, optional): Filtra por jugador.

        Returns:
            int: Numero de partidas exportadas.
        """
        partidas = self.ver_historial(jugador=jugador)
        carpeta = os.path.dirname(ruta)
        if carpeta:
            os.makedirs(carpeta, exist_ok=True)

        campos = ['id', 'jugador', 'fecha', 'puntos_finales', 'victoria']
        with open(ruta, "w", newline="", encoding="utf-8") as archivo:
            escritor = csv.DictWriter(archivo, fieldnames=campos)
            escritor.writeheader()
            escritor.writerows(partidas)

        logger.info("Exportadas %d partidas a %s", len(partidas), ruta)
        return len(partidas)

    @staticmethod
    def _fila_partida(fila):
        return {
            'id': fila['id'],
            'jugador': fila['jugador'],
            'fecha': fila['fecha'],
            'puntos_finales': fila['puntos_finales'],
            'victoria': bool(fila['victoria']),
        }
