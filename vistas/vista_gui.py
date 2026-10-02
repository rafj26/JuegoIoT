import tkinter as tk
from tkinter import ttk, messagebox


# Vista grafica usando Tkinter
class VistaGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Seguridad IoT")
        self.root.geometry("900x700")
        self.root.configure(bg="#1a1a2e")

        # Variables de control
        self.alertas_seleccionadas = []
        self.checkboxes = []
        self.decision_tomada = False

        # Crear interfaz
        self._crear_interfaz()

    def _crear_interfaz(self):
        # Frame principal
        self.frame_principal = tk.Frame(self.root, bg="#1a1a2e")
        self.frame_principal.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Titulo
        self.label_titulo = tk.Label(
            self.frame_principal,
            text="SISTEMA DE SEGURIDAD IoT",
            font=("Arial", 20, "bold"),
            bg="#1a1a2e",
            fg="#00ff88"
        )
        self.label_titulo.pack(pady=10)

        # Frame de informacion superior
        self.frame_info = tk.Frame(self.frame_principal, bg="#16213e", relief=tk.RIDGE, bd=2)
        self.frame_info.pack(fill=tk.X, pady=10)

        # Labels de informacion
        self.label_ronda = tk.Label(
            self.frame_info,
            text="Ronda: 0/5",
            font=("Arial", 12, "bold"),
            bg="#16213e",
            fg="#ffffff"
        )
        self.label_ronda.pack(side=tk.LEFT, padx=20, pady=10)

        self.label_puntos = tk.Label(
            self.frame_info,
            text="Puntos: 15",
            font=("Arial", 12, "bold"),
            bg="#16213e",
            fg="#ffd700"
        )
        self.label_puntos.pack(side=tk.LEFT, padx=20, pady=10)

        self.label_hora = tk.Label(
            self.frame_info,
            text="Hora: 08:00",
            font=("Arial", 12, "bold"),
            bg="#16213e",
            fg="#00d9ff"
        )
        self.label_hora.pack(side=tk.LEFT, padx=20, pady=10)

        # Frame de alertas (con scroll)
        self.frame_alertas_container = tk.Frame(self.frame_principal, bg="#1a1a2e")
        self.frame_alertas_container.pack(fill=tk.BOTH, expand=True, pady=10)

        # Canvas y scrollbar para alertas
        self.canvas = tk.Canvas(self.frame_alertas_container, bg="#1a1a2e", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.frame_alertas_container, orient="vertical", command=self.canvas.yview)
        self.frame_alertas = tk.Frame(self.canvas, bg="#1a1a2e")

        self.frame_alertas.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.frame_alertas, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Frame de botones
        self.frame_botones = tk.Frame(self.frame_principal, bg="#1a1a2e")
        self.frame_botones.pack(fill=tk.X, pady=10)

        self.btn_confirmar = tk.Button(
            self.frame_botones,
            text="CONFIRMAR DECISIÓN",
            font=("Arial", 12, "bold"),
            bg="#00ff88",
            fg="#000000",
            command=self._confirmar_decision,
            width=25,
            height=2
        )
        self.btn_confirmar.pack(pady=10)

    def mostrar_bienvenida(self, info_inicial):
        # Muestra dialogo de bienvenida
        mensaje = f"""
        Bienvenido al Sistema de Seguridad IoT

        Puntos iniciales: {info_inicial['puntos_iniciales']}
        Rondas totales: {info_inicial['total_rondas']}
        Objetivo: Mantener {info_inicial['puntos_victoria']} o más puntos

        REGLAS:
        • Alerta real atendida: +{info_inicial['reglas']['alerta_real_atendida']} puntos
        • Alerta falsa atendida: {info_inicial['reglas']['alerta_falsa_atendida']} punto
        • Alerta real NO atendida: {info_inicial['reglas']['alerta_real_no_atendida']} puntos
        • Alerta falsa NO atendida: {info_inicial['reglas']['alerta_falsa_no_atendida']} puntos
        """
        messagebox.showinfo("Bienvenida", mensaje)

    def actualizar_info_ronda(self, info_ronda):
        # Actualiza labels de informacion
        self.label_ronda.config(text=f"Ronda: {info_ronda['numero']}/{info_ronda['total']}")
        self.label_puntos.config(text=f"Puntos: {info_ronda['puntos']}")

    def mostrar_alertas(self, alertas, hora):
        # Limpia alertas anteriores
        for widget in self.frame_alertas.winfo_children():
            widget.destroy()

        self.checkboxes = []
        self.alertas_seleccionadas = []

        # Actualiza hora
        self.label_hora.config(text=f"Hora: {hora.strftime('%H:%M')}")

        # Crea card para cada alerta
        for alerta in alertas:
            self._crear_card_alerta(alerta)

        self.decision_tomada = False
        self.btn_confirmar.config(state=tk.NORMAL)

    def _crear_card_alerta(self, info):
        # Crea un card para una alerta
        card = tk.Frame(self.frame_alertas, bg="#16213e", relief=tk.RAISED, bd=2)
        card.pack(fill=tk.X, padx=10, pady=5)

        # Variable para checkbox
        var = tk.IntVar()

        # Checkbox
        checkbox = tk.Checkbutton(
            card,
            text="",
            variable=var,
            bg="#16213e",
            fg="#ffffff",
            selectcolor="#000000",
            activebackground="#16213e"
        )
        checkbox.pack(side=tk.LEFT, padx=10)

        # Frame de contenido
        frame_contenido = tk.Frame(card, bg="#16213e")
        frame_contenido.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Encabezado
        label_encabezado = tk.Label(
            frame_contenido,
            text=f"[{info['indice']}] {info['hora']} | {info['tipo']}",
            font=("Arial", 11, "bold"),
            bg="#16213e",
            fg="#00ff88",
            anchor="w"
        )
        label_encabezado.pack(fill=tk.X)

        # Ubicacion
        label_ubicacion = tk.Label(
            frame_contenido,
            text=f"Ubicación: {info['ubicacion']}",
            font=("Arial", 10),
            bg="#16213e",
            fg="#ffffff",
            anchor="w"
        )
        label_ubicacion.pack(fill=tk.X)

        # Mensaje
        label_mensaje = tk.Label(
            frame_contenido,
            text=f"Alerta: {info['mensaje']}",
            font=("Arial", 10),
            bg="#16213e",
            fg="#ffd700",
            anchor="w"
        )
        label_mensaje.pack(fill=tk.X)

        # ID
        label_id = tk.Label(
            frame_contenido,
            text=f"ID: {info['id']}",
            font=("Arial", 9),
            bg="#16213e",
            fg="#888888",
            anchor="w"
        )
        label_id.pack(fill=tk.X)

        # Guardar checkbox
        self.checkboxes.append((var, info['indice']))

    def _confirmar_decision(self):
        # Obtiene las alertas seleccionadas
        self.alertas_seleccionadas = [
            indice for var, indice in self.checkboxes if var.get() == 1
        ]
        self.decision_tomada = True
        self.btn_confirmar.config(state=tk.DISABLED)

    def esperar_decision(self):
        # Espera a que el usuario confirme
        self.decision_tomada = False
        self.root.wait_variable(self._get_variable_espera())
        return self.alertas_seleccionadas

    def _get_variable_espera(self):
        # Crea variable para esperar decision
        self.root.wait_window()
        return None

    def obtener_decision(self):
        # Retorna la decision actual
        return self.alertas_seleccionadas

    def esta_decision_tomada(self):
        # Verifica si se tomo decision
        return self.decision_tomada

    def mostrar_resultados_ronda(self, resultados, puntos_totales):
        # Limpia alertas
        for widget in self.frame_alertas.winfo_children():
            widget.destroy()

        # Titulo de resultados
        label_titulo_resultados = tk.Label(
            self.frame_alertas,
            text="RESULTADOS DE LA RONDA",
            font=("Arial", 14, "bold"),
            bg="#1a1a2e",
            fg="#00ff88"
        )
        label_titulo_resultados.pack(pady=10)

        # Muestra cada resultado
        for resultado in resultados:
            self._crear_card_resultado(resultado)

        # Puntos totales
        label_total = tk.Label(
            self.frame_alertas,
            text=f"PUNTOS TOTALES: {puntos_totales}",
            font=("Arial", 14, "bold"),
            bg="#1a1a2e",
            fg="#ffd700"
        )
        label_total.pack(pady=20)

        # Actualiza puntos en header
        self.label_puntos.config(text=f"Puntos: {puntos_totales}")

        # Boton para continuar
        btn_continuar = tk.Button(
            self.frame_alertas,
            text="CONTINUAR",
            font=("Arial", 12, "bold"),
            bg="#00d9ff",
            fg="#000000",
            command=lambda: self._marcar_continuar(),
            width=20,
            height=2
        )
        btn_continuar.pack(pady=10)

        self.continuar_presionado = False

    def _crear_card_resultado(self, resultado):
        # Crea card de resultado
        accion = "ATENDIDA" if resultado['atendida'] else "IGNORADA"
        tipo = "REAL" if resultado['es_real'] else "FALSA"
        cambio = resultado['cambio_puntos']
        signo = "+" if cambio > 0 else ""

        # Color segun resultado
        if cambio > 0:
            color_fondo = "#1b5e20"
        elif cambio < 0:
            color_fondo = "#b71c1c"
        else:
            color_fondo = "#424242"

        card = tk.Frame(self.frame_alertas, bg=color_fondo, relief=tk.RAISED, bd=2)
        card.pack(fill=tk.X, padx=10, pady=3)

        texto = f"[{resultado['indice']}] {accion} | {tipo} | {signo}{cambio} pts | {resultado['descripcion']}"

        label = tk.Label(
            card,
            text=texto,
            font=("Arial", 10),
            bg=color_fondo,
            fg="#ffffff",
            anchor="w",
            padx=10,
            pady=8
        )
        label.pack(fill=tk.X)

    def _marcar_continuar(self):
        # Marca que se presiono continuar
        self.continuar_presionado = True

    def esperar_continuar(self):
        # Espera a que presionen continuar
        self.continuar_presionado = False
        while not self.continuar_presionado:
            self.root.update()

    def mostrar_resultado_final(self, resultado):
        # Muestra dialogo de resultado final
        if resultado['victoria']:
            titulo = "¡VICTORIA!"
            icono = messagebox.INFO
        else:
            titulo = "DERROTA"
            icono = messagebox.WARNING

        mensaje = f"""
        Puntuación final: {resultado['puntos_finales']} puntos

        {resultado['mensaje']}
        """

        messagebox.showinfo(titulo, mensaje, icon=icono)
        self.root.quit()

    def actualizar(self):
        # Actualiza la ventana
        self.root.update()