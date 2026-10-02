import tkinter as tk
from tkinter import font as tkfont
from tkinter import messagebox, ttk

from vistas.preferencias import Preferencias


# Paletas de colores (contraste de texto >= 4.5:1 sobre su fondo)
TEMAS = {
    'oscuro': {
        'fondo': "#0f172a",
        'superficie': "#1e293b",
        'superficie_alta': "#334155",
        'borde': "#475569",
        'texto': "#f1f5f9",
        'texto_suave': "#cbd5e1",
        'acento': "#38bdf8",
        'texto_acento': "#0f172a",
        'exito': "#22c55e",
        'error': "#f87171",
        'aviso': "#fbbf24",
        'fondo_exito': "#14532d",
        'fondo_error': "#7f1d1d",
        'fondo_neutro': "#334155",
        'seleccion': "#0c4a6e",
    },
    'claro': {
        'fondo': "#f1f5f9",
        'superficie': "#ffffff",
        'superficie_alta': "#e2e8f0",
        'borde': "#94a3b8",
        'texto': "#0f172a",
        'texto_suave': "#334155",
        'acento': "#0369a1",
        'texto_acento': "#ffffff",
        'exito': "#15803d",
        'error': "#b91c1c",
        'aviso': "#b45309",
        'fondo_exito': "#dcfce7",
        'fondo_error': "#fee2e2",
        'fondo_neutro': "#e2e8f0",
        'seleccion': "#bae6fd",
    },
}

# Icono (simbolo) y color de insignia por tipo de dispositivo
ICONOS_DISPOSITIVO = {
    "Sensor de Movimiento": ("⇆", "#a855f7"),
    "Sensor de Temperatura": ("℃", "#f97316"),
    "Sensor de Energia": ("ϟ", "#eab308"),
    "Sensor RFID": ("ID", "#14b8a6"),
    "Sensor de Ruido": ("♪", "#ec4899"),
    "Camara": ("◉", "#6366f1"),
    "Router": ("⇅", "#0ea5e9"),
    "Cerradura Inteligente": ("⊡", "#84cc16"),
}
ICONO_GENERICO = ("?", "#64748b")

FUENTES_PREFERIDAS = ("Segoe UI", "Inter", "Ubuntu", "Noto Sans",
                      "DejaVu Sans", "Liberation Sans", "Helvetica")

ESTADOS = ('info', 'cargando', 'exito', 'error')


# Vista grafica usando Tkinter (dirigida por eventos)
class VistaGUI:
    def __init__(self, root, preferencias=None):
        self.root = root
        self.prefs = preferencias or Preferencias()
        self.colores = TEMAS.get(self.prefs['tema'], TEMAS['oscuro'])

        # Estado de la pantalla actual
        self.alertas = []
        self.seleccion = set()
        self.cursor = 0
        self.cards = []
        self.pausado = False
        self._pantalla = None
        self._accion_enter = None
        self._on_confirmar = None
        self._animaciones = {'contenido': [], 'cabecera': []}
        self._en_transicion = False
        self._puntos_mostrados = None

        self._configurar_ventana()
        self._crear_fuentes()
        self._crear_interfaz()
        self._configurar_atajos()

    # ------------------------------------------------------------------
    # Construccion de la ventana
    # ------------------------------------------------------------------
    def _configurar_ventana(self):
        self.root.title("Sistema de Seguridad IoT")
        self.root.geometry(self.prefs['geometria'])
        self.root.minsize(720, 560)
        self.root.attributes("-fullscreen", self.prefs['pantalla_completa'])
        self.root.protocol("WM_DELETE_WINDOW", self.cerrar)

    def _crear_fuentes(self):
        disponibles = set(tkfont.families(self.root))
        familia = next((f for f in FUENTES_PREFERIDAS if f in disponibles), "TkDefaultFont")
        self.fuentes = {
            'titulo': tkfont.Font(family=familia, size=22, weight="bold"),
            'subtitulo': tkfont.Font(family=familia, size=15, weight="bold"),
            'normal': tkfont.Font(family=familia, size=11),
            'negrita': tkfont.Font(family=familia, size=11, weight="bold"),
            'pequena': tkfont.Font(family=familia, size=10),
            'icono': tkfont.Font(family=familia, size=16, weight="bold"),
            'grande': tkfont.Font(family=familia, size=40, weight="bold"),
        }

    def _crear_interfaz(self):
        c = self.colores
        self.root.configure(bg=c['fondo'])
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(2, weight=1)

        self._crear_estilos()

        # Encabezado
        self.frame_header = tk.Frame(self.root, bg=c['fondo'])
        self.frame_header.grid(row=0, column=0, sticky="ew", padx=24, pady=(18, 6))
        self.frame_header.columnconfigure(0, weight=1)

        self.label_titulo = tk.Label(self.frame_header, text="SISTEMA DE SEGURIDAD IoT",
                                     font=self.fuentes['titulo'], bg=c['fondo'], fg=c['acento'])
        self.label_titulo.grid(row=0, column=0, sticky="w")

        frame_acciones = tk.Frame(self.frame_header, bg=c['fondo'])
        frame_acciones.grid(row=0, column=1, sticky="e")
        self.btn_pausa = self._crear_boton(frame_acciones, "Pausa (P)", self.alternar_pausa, secundario=True)
        self.btn_pausa.pack(side=tk.LEFT, padx=4)
        self._crear_boton(frame_acciones, "Tema (T)", self.alternar_tema, secundario=True).pack(side=tk.LEFT, padx=4)
        self._crear_boton(frame_acciones, "Pantalla (F11)", self.alternar_pantalla_completa,
                          secundario=True).pack(side=tk.LEFT, padx=4)

        # Barra de informacion
        self.frame_info = tk.Frame(self.root, bg=c['superficie'], highlightthickness=1,
                                   highlightbackground=c['borde'])
        self.frame_info.grid(row=1, column=0, sticky="ew", padx=24, pady=6)
        for col in range(3):
            self.frame_info.columnconfigure(col, weight=1)

        self.label_ronda = self._crear_dato(self.frame_info, 0, "Ronda", "-", c['texto'])
        self.label_puntos = self._crear_dato(self.frame_info, 1, "Puntos", "-", c['aviso'])
        self.label_hora = self._crear_dato(self.frame_info, 2, "Hora", "--:--", c['acento'])

        self.barra_progreso = ttk.Progressbar(self.frame_info, style="Rondas.Horizontal.TProgressbar",
                                              mode="determinate", maximum=100)
        self.barra_progreso.grid(row=2, column=0, columnspan=3, sticky="ew", padx=16, pady=(0, 12))

        # Area central con scroll
        self.frame_contenedor = tk.Frame(self.root, bg=c['fondo'])
        self.frame_contenedor.grid(row=2, column=0, sticky="nsew", padx=24, pady=6)
        self.frame_contenedor.rowconfigure(0, weight=1)
        self.frame_contenedor.columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(self.frame_contenedor, bg=c['fondo'], highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.frame_contenedor, orient="vertical",
                                       command=self.canvas.yview, style="Vertical.TScrollbar")
        self.frame_contenido = tk.Frame(self.canvas, bg=c['fondo'])
        self._ventana_contenido = self.canvas.create_window((0, 0), window=self.frame_contenido, anchor="nw")

        self.frame_contenido.bind("<Configure>", self._actualizar_scroll)
        self.canvas.bind("<Configure>", self._ajustar_ancho_contenido)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")

        # Barra inferior: boton principal + estado
        self.frame_pie = tk.Frame(self.root, bg=c['fondo'])
        self.frame_pie.grid(row=3, column=0, sticky="ew", padx=24, pady=(6, 4))
        self.frame_pie.columnconfigure(0, weight=1)

        self.label_ayuda = tk.Label(self.frame_pie, text="", font=self.fuentes['pequena'],
                                    bg=c['fondo'], fg=c['texto_suave'], anchor="w", justify=tk.LEFT)
        self.label_ayuda.grid(row=0, column=0, sticky="ew")

        self.btn_principal = self._crear_boton(self.frame_pie, "", lambda: None)
        self.btn_principal.grid(row=0, column=1, sticky="e")

        self.frame_estado = tk.Frame(self.root, bg=c['superficie'])
        self.frame_estado.grid(row=4, column=0, sticky="ew")
        self.indicador_estado = tk.Canvas(self.frame_estado, width=14, height=14,
                                          bg=c['superficie'], highlightthickness=0)
        self.indicador_estado.pack(side=tk.LEFT, padx=(24, 6), pady=6)
        self.label_estado = tk.Label(self.frame_estado, text="", font=self.fuentes['pequena'],
                                     bg=c['superficie'], fg=c['texto_suave'])
        self.label_estado.pack(side=tk.LEFT, pady=6)

        # Capa de pausa (oculta por defecto)
        self.frame_pausa = tk.Frame(self.root, bg=c['superficie'], highlightthickness=2,
                                    highlightbackground=c['acento'])
        tk.Label(self.frame_pausa, text="PAUSA", font=self.fuentes['grande'],
                 bg=c['superficie'], fg=c['acento']).pack(padx=60, pady=(30, 6))
        tk.Label(self.frame_pausa, text="El juego esta detenido. Pulsa P para continuar.",
                 font=self.fuentes['normal'], bg=c['superficie'], fg=c['texto']).pack(padx=40)
        self._crear_boton(self.frame_pausa, "Reanudar", self.alternar_pausa).pack(pady=24)

    def _crear_estilos(self):
        c = self.colores
        estilo = ttk.Style(self.root)
        estilo.theme_use("clam")
        estilo.configure("Rondas.Horizontal.TProgressbar", troughcolor=c['superficie_alta'],
                         background=c['acento'], bordercolor=c['superficie'],
                         lightcolor=c['acento'], darkcolor=c['acento'], thickness=10)
        estilo.configure("Vertical.TScrollbar", troughcolor=c['fondo'], background=c['superficie_alta'],
                         bordercolor=c['fondo'], arrowcolor=c['texto'])

    def _crear_dato(self, padre, columna, titulo, valor, color):
        c = self.colores
        frame = tk.Frame(padre, bg=c['superficie'])
        frame.grid(row=0, column=columna, sticky="ew", padx=16, pady=(10, 6))
        tk.Label(frame, text=titulo.upper(), font=self.fuentes['pequena'],
                 bg=c['superficie'], fg=c['texto_suave']).pack(anchor="w")
        label = tk.Label(frame, text=valor, font=self.fuentes['subtitulo'], bg=c['superficie'], fg=color)
        label.pack(anchor="w")
        return label

    def _crear_boton(self, padre, texto, comando, secundario=False, color=None):
        c = self.colores
        fondo = color or (c['superficie_alta'] if secundario else c['acento'])
        texto_color = c['texto'] if secundario else c['texto_acento']
        boton = tk.Button(padre, text=texto, command=comando, relief=tk.FLAT, cursor="hand2",
                          font=self.fuentes['negrita'] if not secundario else self.fuentes['pequena'],
                          bg=fondo, fg=texto_color, activebackground=c['borde'],
                          activeforeground=c['texto'], padx=18 if not secundario else 10,
                          pady=10 if not secundario else 4, bd=0, highlightthickness=0)
        return boton

    def _configurar_atajos(self):
        self.root.bind("<Return>", lambda e: self._tecla_enter())
        self.root.bind("<KP_Enter>", lambda e: self._tecla_enter())
        self.root.bind("<space>", lambda e: self._tecla_espacio())
        self.root.bind("<Up>", lambda e: self._mover_cursor(-1))
        self.root.bind("<Down>", lambda e: self._mover_cursor(1))
        self.root.bind("<Key>", self._tecla_numero)
        self.root.bind("<p>", lambda e: self.alternar_pausa())
        self.root.bind("<P>", lambda e: self.alternar_pausa())
        self.root.bind("<t>", lambda e: self.alternar_tema())
        self.root.bind("<T>", lambda e: self.alternar_tema())
        self.root.bind("<F11>", lambda e: self.alternar_pantalla_completa())
        self.root.bind("<Escape>", lambda e: self._salir_pantalla_completa())
        self.root.bind("<Control-q>", lambda e: self.cerrar())
        self.root.bind_all("<MouseWheel>", self._rueda_raton)
        self.root.bind_all("<Button-4>", lambda e: self._desplazar(-1))
        self.root.bind_all("<Button-5>", lambda e: self._desplazar(1))

    # ------------------------------------------------------------------
    # Scroll y redimensionado
    # ------------------------------------------------------------------
    def _actualizar_scroll(self, _evento=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _ajustar_ancho_contenido(self, evento):
        self.canvas.itemconfigure(self._ventana_contenido, width=evento.width)
        ancho_texto = max(200, evento.width - 140)
        for card in self.cards:
            card['mensaje'].configure(wraplength=ancho_texto)

    def _rueda_raton(self, evento):
        self._desplazar(-1 if evento.delta > 0 else 1)

    def _desplazar(self, pasos):
        if self.canvas.yview() != (0.0, 1.0):
            self.canvas.yview_scroll(pasos, "units")

    def _limpiar_contenido(self):
        self._cancelar_animaciones()
        for widget in self.frame_contenido.winfo_children():
            widget.destroy()
        self.cards = []
        self.canvas.yview_moveto(0)

    # ------------------------------------------------------------------
    # Estado, animaciones y utilidades
    # ------------------------------------------------------------------
    def mostrar_estado(self, mensaje, tipo='info'):
        # Indicador visual de estado: info, cargando, exito o error
        c = self.colores
        color = {'info': c['acento'], 'cargando': c['aviso'],
                 'exito': c['exito'], 'error': c['error']}.get(tipo, c['acento'])
        self.indicador_estado.delete("all")
        self.indicador_estado.create_oval(2, 2, 12, 12, fill=color, outline=color)
        self.label_estado.configure(text=mensaje)
        self.estado_actual = (mensaje, tipo)

    def _programar(self, ms, funcion, grupo='contenido'):
        # Programa una funcion; el grupo permite cancelar solo las del contenido
        identificador = self.root.after(ms if self.prefs['animaciones'] else 0, funcion)
        self._animaciones[grupo].append(identificador)
        return identificador

    def _cancelar_animaciones(self, grupos=('contenido',)):
        for grupo in grupos:
            for identificador in self._animaciones[grupo]:
                try:
                    self.root.after_cancel(identificador)
                except tk.TclError:
                    pass
            self._animaciones[grupo] = []

    def _animar_progreso(self, destino):
        self._progreso_objetivo = destino
        actual = self.barra_progreso['value']
        if not self.prefs['animaciones'] or abs(destino - actual) < 1:
            self.barra_progreso['value'] = destino
            return
        self.barra_progreso['value'] = actual + (destino - actual) * 0.25
        self._programar(16, lambda: self._animar_progreso(destino), 'cabecera')

    def _animar_puntos(self, destino):
        self._puntos_objetivo = destino
        actual = self._puntos_mostrados
        if actual is None or not self.prefs['animaciones'] or actual == destino:
            self._puntos_mostrados = destino
            self._pintar_puntos(destino)
            return
        paso = 1 if destino > actual else -1
        self._puntos_mostrados = actual + paso
        self._pintar_puntos(self._puntos_mostrados)
        self._programar(60, lambda: self._animar_puntos(destino), 'cabecera')

    def _pintar_puntos(self, puntos):
        c = self.colores
        objetivo = getattr(self, 'puntos_victoria', 0)
        color = c['exito'] if puntos >= objetivo else c['error']
        self.label_puntos.configure(text=str(puntos), fg=color)

    def _configurar_pie(self, ayuda, texto_boton, accion):
        self.label_ayuda.configure(text=ayuda)
        self._accion_enter = accion
        if texto_boton:
            self.btn_principal.configure(text=texto_boton, command=accion, state=tk.NORMAL)
            self.btn_principal.grid()
        else:
            self.btn_principal.grid_remove()

    def _registrar_pantalla(self, funcion, *args):
        # Recuerda la pantalla actual para poder redibujarla al cambiar el tema
        self._pantalla = (funcion, args)

    # ------------------------------------------------------------------
    # Pantallas
    # ------------------------------------------------------------------
    def mostrar_bienvenida(self, info_inicial, on_iniciar):
        # Pantalla de bienvenida con reglas, nombre del jugador y opciones
        self._registrar_pantalla(self.mostrar_bienvenida, info_inicial, on_iniciar)
        self._limpiar_contenido()
        c = self.colores
        self.puntos_victoria = info_inicial['puntos_victoria']
        self.total_rondas = info_inicial['total_rondas']
        self.label_ronda.configure(text=f"0/{self.total_rondas}")
        self._puntos_mostrados = info_inicial['puntos_iniciales']
        self._pintar_puntos(self._puntos_mostrados)
        self.barra_progreso['value'] = 0

        tarjeta = tk.Frame(self.frame_contenido, bg=c['superficie'], highlightthickness=1,
                           highlightbackground=c['borde'])
        tarjeta.pack(fill=tk.X, padx=4, pady=8)

        tk.Label(tarjeta, text="Bienvenido, administrador de red", font=self.fuentes['subtitulo'],
                 bg=c['superficie'], fg=c['texto']).pack(anchor="w", padx=24, pady=(20, 4))
        tk.Label(tarjeta,
                 text=(f"Analiza las alertas de {info_inicial['total_rondas']} rondas y decide cuales "
                       f"atender. Empiezas con {info_inicial['puntos_iniciales']} puntos y necesitas "
                       f"{info_inicial['puntos_victoria']} o mas al final para ganar."),
                 font=self.fuentes['normal'], bg=c['superficie'], fg=c['texto_suave'],
                 wraplength=760, justify=tk.LEFT).pack(anchor="w", padx=24)

        reglas = info_inicial['reglas']
        frame_reglas = tk.Frame(tarjeta, bg=c['superficie'])
        frame_reglas.pack(fill=tk.X, padx=24, pady=16)
        filas = [
            ("Alerta real atendida", reglas['alerta_real_atendida']),
            ("Alerta falsa atendida", reglas['alerta_falsa_atendida']),
            ("Alerta real ignorada", reglas['alerta_real_no_atendida']),
            ("Alerta falsa ignorada", reglas['alerta_falsa_no_atendida']),
        ]
        for i, (texto, valor) in enumerate(filas):
            color = c['exito'] if valor > 0 else c['error'] if valor < 0 else c['texto_suave']
            tk.Label(frame_reglas, text=texto, font=self.fuentes['normal'], bg=c['superficie'],
                     fg=c['texto']).grid(row=i, column=0, sticky="w", pady=2)
            tk.Label(frame_reglas, text=f"{valor:+d}", font=self.fuentes['negrita'], bg=c['superficie'],
                     fg=color).grid(row=i, column=1, sticky="e", padx=24)

        # Opciones del jugador
        frame_opciones = tk.Frame(tarjeta, bg=c['superficie'])
        frame_opciones.pack(fill=tk.X, padx=24, pady=(0, 20))
        tk.Label(frame_opciones, text="Nombre del jugador", font=self.fuentes['negrita'],
                 bg=c['superficie'], fg=c['texto']).grid(row=0, column=0, sticky="w")
        self.var_jugador = tk.StringVar(value=self.prefs['jugador'])
        entrada = tk.Entry(frame_opciones, textvariable=self.var_jugador, font=self.fuentes['normal'],
                           bg=c['superficie_alta'], fg=c['texto'], insertbackground=c['texto'],
                           relief=tk.FLAT, width=24)
        entrada.grid(row=0, column=1, sticky="w", padx=12, ipady=4)

        self.var_confirmar = tk.BooleanVar(value=self.prefs['confirmar_decision'])
        self.var_animaciones = tk.BooleanVar(value=self.prefs['animaciones'])
        for fila, (texto, variable) in enumerate(
                [("Pedir confirmacion antes de decidir", self.var_confirmar),
                 ("Animaciones", self.var_animaciones)], start=1):
            tk.Checkbutton(frame_opciones, text=texto, variable=variable, font=self.fuentes['normal'],
                           bg=c['superficie'], fg=c['texto'], selectcolor=c['superficie_alta'],
                           activebackground=c['superficie'], activeforeground=c['texto'],
                           highlightthickness=0).grid(row=fila, column=0, columnspan=2, sticky="w", pady=2)

        self._crear_seccion_atajos()

        def iniciar():
            self.prefs['jugador'] = self.var_jugador.get().strip() or "Jugador"
            self.prefs['confirmar_decision'] = self.var_confirmar.get()
            self.prefs['animaciones'] = self.var_animaciones.get()
            self.prefs.guardar()
            on_iniciar(self.prefs['jugador'])

        self._configurar_pie("Pulsa Enter para comenzar", "COMENZAR", iniciar)
        self.mostrar_estado("Listo para comenzar")

    def _crear_seccion_atajos(self):
        c = self.colores
        tarjeta = tk.Frame(self.frame_contenido, bg=c['superficie'], highlightthickness=1,
                           highlightbackground=c['borde'])
        tarjeta.pack(fill=tk.X, padx=4, pady=8)
        tk.Label(tarjeta, text="Atajos de teclado", font=self.fuentes['negrita'],
                 bg=c['superficie'], fg=c['texto']).pack(anchor="w", padx=24, pady=(14, 4))
        atajos = [("1-9", "Marcar / desmarcar alerta"), ("Flechas + Espacio", "Mover y marcar"),
                  ("Enter", "Confirmar / continuar"), ("P", "Pausar / reanudar"),
                  ("T", "Cambiar tema"), ("F11 / Esc", "Pantalla completa")]
        frame = tk.Frame(tarjeta, bg=c['superficie'])
        frame.pack(fill=tk.X, padx=24, pady=(0, 14))
        for i, (tecla, accion) in enumerate(atajos):
            tk.Label(frame, text=tecla, font=self.fuentes['negrita'], bg=c['superficie_alta'],
                     fg=c['texto'], padx=8).grid(row=i // 2, column=(i % 2) * 2, sticky="w", pady=3)
            tk.Label(frame, text=accion, font=self.fuentes['pequena'], bg=c['superficie'],
                     fg=c['texto_suave']).grid(row=i // 2, column=(i % 2) * 2 + 1, sticky="w", padx=(8, 32))

    def mostrar_transicion(self, numero_ronda, on_terminar):
        # Animacion corta entre rondas
        self._pantalla = None
        self._limpiar_contenido()
        self._en_transicion = True
        self._configurar_pie("", "", None)
        self.mostrar_estado(f"Preparando ronda {numero_ronda}...", 'cargando')
        c = self.colores
        label = tk.Label(self.frame_contenido, text=f"RONDA {numero_ronda}", font=self.fuentes['grande'],
                         bg=c['fondo'], fg=c['fondo'])
        label.pack(pady=120)

        pasos = 8
        inicio = self._a_rgb(c['fondo'])
        fin = self._a_rgb(c['acento'])

        def paso(i):
            if i > pasos:
                self._programar(250, terminar)
                return
            t = i / pasos
            color = "#%02x%02x%02x" % tuple(int(a + (b - a) * t) for a, b in zip(inicio, fin))
            label.configure(fg=color)
            self._programar(35, lambda: paso(i + 1))

        def terminar():
            self._en_transicion = False
            on_terminar()

        if self.prefs['animaciones']:
            paso(0)
        else:
            terminar()

    def actualizar_info_ronda(self, info_ronda):
        # Actualiza ronda, puntos y barra de progreso
        self.total_rondas = info_ronda['total']
        self.label_ronda.configure(text=f"{info_ronda['numero']}/{info_ronda['total']}")
        self._animar_puntos(info_ronda['puntos'])
        self._animar_progreso(100 * (info_ronda['numero'] - 1) / info_ronda['total'])

    def mostrar_alertas(self, alertas, hora, on_confirmar):
        # Muestra las alertas como tarjetas seleccionables
        self._registrar_pantalla(self.mostrar_alertas, alertas, hora, on_confirmar)
        self._limpiar_contenido()
        self.alertas = alertas
        self._on_confirmar = on_confirmar
        self.cursor = 0
        self.label_hora.configure(text=hora.strftime('%H:%M'))

        for i, alerta in enumerate(alertas):
            self._programar(45 * i, lambda a=alerta: self._crear_card_alerta(a))
        self._programar(45 * len(alertas), self._pintar_seleccion)

        self._configurar_pie("Selecciona las alertas que quieres atender (1-9, clic o Espacio). "
                             "Las no marcadas se ignoran.",
                             "CONFIRMAR DECISION", self._confirmar_decision)
        self.mostrar_estado(f"{len(alertas)} alertas recibidas a las {hora.strftime('%H:%M')}")

    def _crear_card_alerta(self, alerta):
        c = self.colores
        indice = alerta['indice']
        simbolo, color_icono = ICONOS_DISPOSITIVO.get(alerta['tipo'], ICONO_GENERICO)

        card = tk.Frame(self.frame_contenido, bg=c['superficie'], highlightthickness=2,
                        highlightbackground=c['superficie'], cursor="hand2")
        card.pack(fill=tk.X, padx=4, pady=4)
        card.columnconfigure(2, weight=1)

        numero = tk.Label(card, text=str(indice), font=self.fuentes['negrita'], width=2,
                          bg=c['superficie_alta'], fg=c['texto'])
        numero.grid(row=0, column=0, rowspan=2, sticky="ns", padx=(10, 8), pady=10)

        icono = tk.Canvas(card, width=40, height=40, bg=c['superficie'], highlightthickness=0)
        icono.create_oval(2, 2, 38, 38, fill=color_icono, outline=color_icono)
        icono.create_text(20, 20, text=simbolo, fill="#ffffff", font=self.fuentes['icono'])
        icono.grid(row=0, column=1, rowspan=2, padx=(0, 12), pady=10)

        encabezado = tk.Label(card, text=f"{alerta['tipo']}  ·  {alerta['ubicacion']}",
                              font=self.fuentes['negrita'], bg=c['superficie'], fg=c['texto'], anchor="w")
        encabezado.grid(row=0, column=2, sticky="ew", pady=(10, 0))

        mensaje = tk.Label(card, text=alerta['mensaje'], font=self.fuentes['normal'], bg=c['superficie'],
                           fg=c['texto_suave'], anchor="w", justify=tk.LEFT,
                           wraplength=max(200, self.canvas.winfo_width() - 140))
        mensaje.grid(row=1, column=2, sticky="ew", pady=(0, 10))

        detalle = tk.Label(card, text=f"{alerta['id']}\n{alerta['hora']}", font=self.fuentes['pequena'],
                           bg=c['superficie'], fg=c['texto_suave'], justify=tk.RIGHT)
        detalle.grid(row=0, column=3, rowspan=2, padx=12)

        estado = tk.Label(card, text="IGNORAR", font=self.fuentes['pequena'], width=9,
                          bg=c['superficie_alta'], fg=c['texto'])
        estado.grid(row=0, column=4, rowspan=2, padx=(0, 12))

        info = {'indice': indice, 'frame': card, 'mensaje': mensaje, 'estado': estado,
                'widgets': [card, encabezado, mensaje, detalle, icono]}
        self.cards.append(info)

        for widget in (card, numero, icono, encabezado, mensaje, detalle, estado):
            widget.bind("<Button-1>", lambda e, i=indice: self.alternar_alerta(i))
        self._pintar_seleccion()

    def alternar_alerta(self, indice):
        # Marca o desmarca una alerta para atenderla
        if self.pausado or self._on_confirmar is None:
            return
        if not any(card['indice'] == indice for card in self.cards):
            return
        self.seleccion.symmetric_difference_update({indice})
        self.cursor = indice - 1
        self._pintar_seleccion()
        self.mostrar_estado(f"{len(self.seleccion)} alerta(s) marcadas para atender")

    def _pintar_seleccion(self):
        c = self.colores
        for posicion, card in enumerate(self.cards):
            seleccionada = card['indice'] in self.seleccion
            fondo = c['seleccion'] if seleccionada else c['superficie']
            borde = c['acento'] if posicion == self.cursor else (c['acento'] if seleccionada else c['superficie'])
            card['frame'].configure(highlightbackground=borde, highlightcolor=borde)
            for widget in card['widgets']:
                widget.configure(bg=fondo)
            card['estado'].configure(text="ATENDER" if seleccionada else "IGNORAR",
                                     bg=c['acento'] if seleccionada else c['superficie_alta'],
                                     fg=c['texto_acento'] if seleccionada else c['texto'])

    def _mover_cursor(self, delta):
        if self.pausado or not self.cards or self._on_confirmar is None:
            return
        self.cursor = (self.cursor + delta) % len(self.cards)
        self._pintar_seleccion()
        # Desplaza la lista solo si la tarjeta queda fuera de la zona visible
        frame = self.cards[self.cursor]['frame']
        self.root.update_idletasks()
        altura = max(1, self.frame_contenido.winfo_height())
        inicio, fin = self.canvas.yview()
        arriba = frame.winfo_y() / altura
        abajo = (frame.winfo_y() + frame.winfo_height()) / altura
        if arriba < inicio:
            self.canvas.yview_moveto(arriba)
        elif abajo > fin:
            self.canvas.yview_moveto(max(0, abajo - (fin - inicio)))

    def _confirmar_decision(self):
        if self.pausado or self._on_confirmar is None:
            return
        seleccion = sorted(self.seleccion)
        if self.prefs['confirmar_decision']:
            ignoradas = len(self.alertas) - len(seleccion)
            texto = (f"Vas a atender {len(seleccion)} alerta(s) e ignorar {ignoradas}.\n\n"
                     "¿Confirmas la decision?")
            if not messagebox.askyesno("Confirmar decision", texto, parent=self.root):
                self.mostrar_estado("Decision cancelada, sigue revisando", 'info')
                return
        callback = self._on_confirmar
        self._on_confirmar = None
        self.seleccion = set()
        self.mostrar_estado("Evaluando decisiones...", 'cargando')
        callback(seleccion)

    def mostrar_resultados_ronda(self, resultados, puntos_totales, historial_puntos, on_continuar):
        # Muestra el resultado de cada alerta y la grafica de puntos
        self._registrar_pantalla(self.mostrar_resultados_ronda, resultados, puntos_totales,
                                 historial_puntos, on_continuar)
        self._limpiar_contenido()
        c = self.colores

        aciertos = sum(1 for r in resultados if r['cambio_puntos'] > 0
                       or (not r['atendida'] and not r['es_real']))
        cambio = sum(r['cambio_puntos'] for r in resultados)

        tk.Label(self.frame_contenido, text="RESULTADOS DE LA RONDA", font=self.fuentes['subtitulo'],
                 bg=c['fondo'], fg=c['texto']).pack(anchor="w", padx=4, pady=(4, 2))
        tk.Label(self.frame_contenido,
                 text=f"Aciertos: {aciertos}/{len(resultados)}   Cambio: {cambio:+d}   Total: {puntos_totales}",
                 font=self.fuentes['normal'], bg=c['fondo'], fg=c['texto_suave']).pack(anchor="w", padx=4)

        for i, resultado in enumerate(resultados):
            self._programar(35 * i, lambda r=resultado: self._crear_card_resultado(r))

        self._programar(35 * len(resultados), lambda: self._crear_grafica(historial_puntos))

        self._animar_puntos(puntos_totales)
        self._animar_progreso(100 * len(historial_puntos[1:]) / max(1, self.total_rondas))

        self._configurar_pie("Pulsa Enter para continuar", "CONTINUAR", on_continuar)
        tipo = 'exito' if cambio >= 0 else 'error'
        self.mostrar_estado(f"Ronda evaluada: {cambio:+d} puntos", tipo)

    def _crear_card_resultado(self, resultado):
        c = self.colores
        cambio = resultado['cambio_puntos']
        if cambio > 0:
            fondo, acento = c['fondo_exito'], c['exito']
        elif cambio < 0:
            fondo, acento = c['fondo_error'], c['error']
        else:
            fondo, acento = c['fondo_neutro'], c['texto_suave']

        card = tk.Frame(self.frame_contenido, bg=fondo)
        card.pack(fill=tk.X, padx=4, pady=3)
        tk.Frame(card, bg=acento, width=6).pack(side=tk.LEFT, fill=tk.Y)

        accion = "ATENDIDA" if resultado['atendida'] else "IGNORADA"
        tipo = "REAL" if resultado['es_real'] else "FALSA"
        tk.Label(card, text=f"[{resultado['indice']}]  {accion}  ·  {tipo}", font=self.fuentes['negrita'],
                 bg=fondo, fg=c['texto'], anchor="w").pack(side=tk.LEFT, padx=10, pady=8)
        tk.Label(card, text=resultado['descripcion'], font=self.fuentes['normal'], bg=fondo,
                 fg=c['texto'], anchor="w").pack(side=tk.LEFT, fill=tk.X, expand=True, pady=8)
        tk.Label(card, text=f"{cambio:+d} pts", font=self.fuentes['negrita'], bg=fondo,
                 fg=c['texto']).pack(side=tk.RIGHT, padx=14, pady=8)

    def _crear_grafica(self, historial_puntos):
        # Grafica de la puntuacion acumulada por ronda
        c = self.colores
        tk.Label(self.frame_contenido, text="Puntuacion por ronda", font=self.fuentes['negrita'],
                 bg=c['fondo'], fg=c['texto']).pack(anchor="w", padx=4, pady=(16, 4))
        grafica = tk.Canvas(self.frame_contenido, height=200, bg=c['superficie'],
                            highlightthickness=1, highlightbackground=c['borde'])
        grafica.pack(fill=tk.X, padx=4, pady=(0, 8))
        grafica.bind("<Configure>", lambda e: self._dibujar_grafica(grafica, historial_puntos))

    def _dibujar_grafica(self, grafica, historial_puntos):
        c = self.colores
        grafica.delete("all")
        ancho = max(grafica.winfo_width(), 300)
        alto = max(grafica.winfo_height(), 150)
        margen_x, margen_y = 48, 24
        total = max(self.total_rondas, len(historial_puntos) - 1, 1)

        valores = list(historial_puntos) + [self.puntos_victoria]
        minimo, maximo = min(valores) - 2, max(valores) + 2
        rango = max(1, maximo - minimo)

        def x(i):
            return margen_x + (ancho - 2 * margen_x) * i / total

        def y(v):
            return alto - margen_y - (alto - 2 * margen_y) * (v - minimo) / rango

        # Ejes y etiquetas
        grafica.create_line(margen_x, alto - margen_y, ancho - margen_x, alto - margen_y, fill=c['borde'])
        for i in range(total + 1):
            grafica.create_text(x(i), alto - margen_y + 12, text="Inicio" if i == 0 else f"R{i}",
                                fill=c['texto_suave'], font=self.fuentes['pequena'])

        # Linea de victoria
        yv = y(self.puntos_victoria)
        grafica.create_line(margen_x, yv, ancho - margen_x, yv, fill=c['aviso'], dash=(6, 4))
        grafica.create_text(margen_x - 8, yv, text=str(self.puntos_victoria), anchor="e",
                            fill=c['aviso'], font=self.fuentes['pequena'])

        # Serie de puntos
        puntos = [(x(i), y(v)) for i, v in enumerate(historial_puntos)]
        if len(puntos) > 1:
            grafica.create_line(*[coord for p in puntos for coord in p], fill=c['acento'], width=3,
                                smooth=False)
        for (px, py), valor in zip(puntos, historial_puntos):
            color = c['exito'] if valor >= self.puntos_victoria else c['error']
            grafica.create_oval(px - 5, py - 5, px + 5, py + 5, fill=color, outline=c['superficie'], width=2)
            grafica.create_text(px, py - 14, text=str(valor), fill=c['texto'], font=self.fuentes['pequena'])

    def mostrar_resultado_final(self, resultado, historial_puntos, on_reiniciar, mensaje_guardado=None):
        # Pantalla final con victoria/derrota y grafica de toda la partida
        self._registrar_pantalla(self.mostrar_resultado_final, resultado, historial_puntos,
                                 on_reiniciar, mensaje_guardado)
        self._limpiar_contenido()
        c = self.colores
        victoria = resultado['victoria']
        color = c['exito'] if victoria else c['error']

        self._animar_progreso(100)
        self._animar_puntos(resultado['puntos_finales'])

        tarjeta = tk.Frame(self.frame_contenido, bg=c['superficie'], highlightthickness=2,
                           highlightbackground=color)
        tarjeta.pack(fill=tk.X, padx=4, pady=8)
        tk.Label(tarjeta, text="¡VICTORIA!" if victoria else "DERROTA", font=self.fuentes['grande'],
                 bg=c['superficie'], fg=color).pack(pady=(24, 4))
        tk.Label(tarjeta, text=f"Puntuacion final: {resultado['puntos_finales']} puntos",
                 font=self.fuentes['subtitulo'], bg=c['superficie'], fg=c['texto']).pack()
        tk.Label(tarjeta, text=resultado['mensaje'], font=self.fuentes['normal'],
                 bg=c['superficie'], fg=c['texto_suave']).pack(pady=(4, 24))

        self._crear_grafica(historial_puntos)

        self._configurar_pie("Enter: jugar de nuevo  ·  Ctrl+Q: salir", "JUGAR DE NUEVO", on_reiniciar)
        if mensaje_guardado:
            self.mostrar_estado(*mensaje_guardado)
        else:
            self.mostrar_estado("Partida terminada", 'exito' if victoria else 'error')

    # ------------------------------------------------------------------
    # Teclado y acciones globales
    # ------------------------------------------------------------------
    def _foco_en_entrada(self):
        return isinstance(self.root.focus_get(), tk.Entry)

    def _tecla_enter(self):
        if self.pausado or self._accion_enter is None:
            return
        self._accion_enter()

    def _tecla_espacio(self):
        if self._foco_en_entrada() or not self.cards or self._on_confirmar is None:
            return
        self.alternar_alerta(self.cards[self.cursor]['indice'])

    def _tecla_numero(self, evento):
        if self._foco_en_entrada():
            return
        caracter = evento.char
        if caracter.isdigit() and caracter != "0":
            self.alternar_alerta(int(caracter))

    def alternar_pausa(self):
        # Pausa o reanuda el juego
        if self._foco_en_entrada():
            return
        self.pausado = not self.pausado
        if self.pausado:
            self.frame_pausa.place(relx=0.5, rely=0.5, anchor="center")
            self.frame_pausa.lift()
            self.btn_principal.configure(state=tk.DISABLED)
            self.btn_pausa.configure(text="Reanudar (P)")
            self._estado_previo = getattr(self, 'estado_actual', ("", 'info'))
            self.mostrar_estado("Juego en pausa", 'cargando')
        else:
            self.frame_pausa.place_forget()
            self.btn_principal.configure(state=tk.NORMAL)
            self.btn_pausa.configure(text="Pausa (P)")
            self.mostrar_estado(*self._estado_previo)

    def alternar_tema(self):
        # Cambia entre tema oscuro y claro y redibuja la pantalla actual
        if self._foco_en_entrada() or self._en_transicion:
            return
        self._cancelar_animaciones(('contenido', 'cabecera'))
        if getattr(self, '_puntos_objetivo', None) is not None:
            self._puntos_mostrados = self._puntos_objetivo
        if getattr(self, '_progreso_objetivo', None) is not None:
            self.barra_progreso['value'] = self._progreso_objetivo
        self.prefs['tema'] = 'claro' if self.prefs['tema'] == 'oscuro' else 'oscuro'
        self.prefs.guardar()
        self.colores = TEMAS[self.prefs['tema']]

        estado = getattr(self, 'estado_actual', ("", 'info'))
        datos = (self.label_ronda.cget("text"), self.label_hora.cget("text"), self.barra_progreso['value'])
        pausado = self.pausado
        for widget in self.root.winfo_children():
            widget.destroy()
        self.cards = []
        self.pausado = False
        self._crear_interfaz()

        self.label_ronda.configure(text=datos[0])
        self.label_hora.configure(text=datos[1])
        self.barra_progreso['value'] = datos[2]
        if self._puntos_mostrados is not None:
            self._pintar_puntos(self._puntos_mostrados)

        if self._pantalla:
            funcion, args = self._pantalla
            seleccion, cursor = set(self.seleccion), self.cursor
            animaciones = self.prefs['animaciones']
            self.prefs['animaciones'] = False
            funcion(*args)
            self.prefs['animaciones'] = animaciones
            if funcion == self.mostrar_alertas:
                self.seleccion, self.cursor = seleccion, cursor
                self._pintar_seleccion()
        self.mostrar_estado(*estado)
        if pausado:
            self.alternar_pausa()

    def alternar_pantalla_completa(self):
        # Activa o desactiva la pantalla completa
        self.prefs['pantalla_completa'] = not self.prefs['pantalla_completa']
        self.root.attributes("-fullscreen", self.prefs['pantalla_completa'])
        self.prefs.guardar()

    def _salir_pantalla_completa(self):
        if self.prefs['pantalla_completa']:
            self.alternar_pantalla_completa()

    def cerrar(self):
        # Guarda preferencias y cierra la ventana
        if not self.prefs['pantalla_completa']:
            self.prefs['geometria'] = self.root.geometry().split("+")[0]
        self.prefs.guardar()
        self._cancelar_animaciones(('contenido', 'cabecera'))
        self.root.destroy()

    @staticmethod
    def _a_rgb(color):
        color = color.lstrip("#")
        return tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))
