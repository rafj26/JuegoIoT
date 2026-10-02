"""Filtros y etiquetas de plantilla del juego."""
from django import template

register = template.Library()

ICONOS = {
    "Sensor de Movimiento": ("⇆", "#a855f7"),
    "Sensor de Temperatura": ("℃", "#f97316"),
    "Sensor de Energia": ("ϟ", "#ca8a04"),
    "Sensor RFID": ("ID", "#0d9488"),
    "Sensor de Ruido": ("♪", "#db2777"),
    "Camara": ("◉", "#6366f1"),
    "Router": ("⇅", "#0284c7"),
    "Cerradura Inteligente": ("⊡", "#65a30d"),
}
ICONO_GENERICO = ("?", "#64748b")


@register.filter
def icono_dispositivo(tipo):
    """Simbolo del tipo de dispositivo."""
    return ICONOS.get(tipo, ICONO_GENERICO)[0]


@register.filter
def color_dispositivo(tipo):
    """Color de la insignia del tipo de dispositivo."""
    return ICONOS.get(tipo, ICONO_GENERICO)[1]


@register.simple_tag
def grafica_puntos(historial, objetivo, total_rondas, ancho=640, alto=220, margen=44):
    """
    Calcula las coordenadas de la grafica SVG de puntos por ronda.

    Args:
        historial (list[int]): Puntos al inicio y despues de cada ronda.
        objetivo (int): Puntos necesarios para ganar.
        total_rondas (int): Numero de rondas del eje X.

    Returns:
        dict: Coordenadas y datos para la plantilla ``_grafica.html``.
    """
    total = max(int(total_rondas), len(historial) - 1, 1)
    valores = list(historial) + [objetivo]
    minimo, maximo = min(valores) - 2, max(valores) + 2
    rango = max(1, maximo - minimo)
    y_base = alto - 30

    def x(i):
        return round(margen + (ancho - 2 * margen) * i / total)

    def y(v):
        return round(y_base - (y_base - 24) * (v - minimo) / rango)

    puntos = [{'x': x(i), 'y': y(v), 'valor': v, 'nombre': "Inicio" if i == 0 else f"R{i}"}
              for i, v in enumerate(historial)]
    return {
        'ancho': ancho, 'alto': alto, 'margen': margen, 'x_fin': ancho - margen,
        'y_base': y_base, 'y_objetivo': y(objetivo), 'puntos': puntos,
        'linea': " ".join(f"{p['x']},{p['y']}" for p in puntos),
    }
