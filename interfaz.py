"""Interfaz grafica moderna y animada para el sistema inteligente de rutas."""

import tkinter as tk
from tkinter import messagebox, ttk

from src.base_conocimiento import ESTACIONES, construir_grafo
from src.busqueda import a_estrella, costo_uniforme, detalle_tramos


BG = "#08111f"
PANEL = "#0f1b2d"
CARD = "#132238"
CARD_2 = "#172a43"
TEXT = "#f8fafc"
MUTED = "#94a3b8"
BLUE = "#3b82f6"
CYAN = "#22d3ee"
GREEN = "#34d399"
AMBER = "#fbbf24"
RED = "#fb7185"
TRACK = "#334155"


class AplicacionRutas:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.grafo = construir_grafo()
        self.ruta_actual: list[str] = []
        self.puntos_ruta: list[tuple[int, int]] = []
        self.animacion_id = 0
        self.vehiculo = None
        self.segmentos_animados: list[int] = []

        self.root.title("Sistema inteligente de rutas - Transmetro")
        self.root.geometry("1280x820")
        self.root.minsize(1120, 720)
        self.root.configure(bg=BG)

        self._configurar_estilos()
        self._crear_interfaz()
        self.root.after(120, self._dibujar_red_base)
        self._animar_estado()

    def _configurar_estilos(self) -> None:
        estilo = ttk.Style()
        try:
            estilo.theme_use("clam")
        except tk.TclError:
            pass

        estilo.configure(
            "Modern.TCombobox",
            fieldbackground="#0b1728",
            background="#0b1728",
            foreground=TEXT,
            arrowcolor=CYAN,
            bordercolor="#263b57",
            lightcolor="#263b57",
            darkcolor="#263b57",
            padding=8,
            font=("Segoe UI", 10),
        )
        estilo.map(
            "Modern.TCombobox",
            fieldbackground=[("readonly", "#0b1728")],
            foreground=[("readonly", TEXT)],
            selectbackground=[("readonly", "#0b1728")],
            selectforeground=[("readonly", TEXT)],
        )

    def _crear_interfaz(self) -> None:
        self._crear_encabezado()

        contenido = tk.Frame(self.root, bg=BG)
        contenido.pack(fill="both", expand=True, padx=22, pady=(0, 22))
        contenido.grid_columnconfigure(0, minsize=305)
        contenido.grid_columnconfigure(1, weight=1)
        contenido.grid_columnconfigure(2, minsize=350)
        contenido.grid_rowconfigure(0, weight=1)

        self._crear_panel_control(contenido)
        self._crear_panel_mapa(contenido)
        self._crear_panel_resultados(contenido)

    def _crear_encabezado(self) -> None:
        header = tk.Frame(self.root, bg=BG, height=118)
        header.pack(fill="x", padx=24, pady=(20, 12))
        header.pack_propagate(False)

        izquierda = tk.Frame(header, bg=BG)
        izquierda.pack(side="left", fill="y")

        titulo_linea = tk.Frame(izquierda, bg=BG)
        titulo_linea.pack(anchor="w")

        tk.Label(
            titulo_linea,
            text="TRANSMETRO",
            bg=BG,
            fg=TEXT,
            font=("Segoe UI", 25, "bold"),
        ).pack(side="left")

        tk.Label(
            titulo_linea,
            text="AI ROUTE",
            bg=BLUE,
            fg="white",
            font=("Segoe UI", 10, "bold"),
            padx=10,
            pady=5,
        ).pack(side="left", padx=(12, 0), pady=(5, 0))

        tk.Label(
            izquierda,
            text="Sistema inteligente basado en reglas y busqueda heuristica",
            bg=BG,
            fg=MUTED,
            font=("Segoe UI", 11),
        ).pack(anchor="w", pady=(8, 0))

        estado = tk.Frame(header, bg=PANEL, padx=14, pady=10)
        estado.pack(side="right", anchor="n", pady=3)

        self.punto_estado = tk.Canvas(
            estado,
            width=14,
            height=14,
            bg=PANEL,
            highlightthickness=0,
        )
        self.punto_estado.pack(side="left", padx=(0, 8))
        self.punto_estado_id = self.punto_estado.create_oval(2, 2, 12, 12, fill=GREEN, outline="")

        tk.Label(
            estado,
            text="Motor de busqueda listo",
            bg=PANEL,
            fg="#dbeafe",
            font=("Segoe UI", 10, "bold"),
        ).pack(side="left")

    def _crear_panel_control(self, padre: tk.Frame) -> None:
        panel = tk.Frame(padre, bg=PANEL, padx=20, pady=20)
        panel.grid(row=0, column=0, sticky="nsew", padx=(0, 14))

        tk.Label(
            panel,
            text="PLANIFICAR VIAJE",
            bg=PANEL,
            fg=CYAN,
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w")

        tk.Label(
            panel,
            text="Encuentra la mejor ruta",
            bg=PANEL,
            fg=TEXT,
            font=("Segoe UI", 18, "bold"),
        ).pack(anchor="w", pady=(5, 4))

        tk.Label(
            panel,
            text="Selecciona el origen y destino para comparar A* con costo uniforme.",
            bg=PANEL,
            fg=MUTED,
            font=("Segoe UI", 9),
            wraplength=250,
            justify="left",
        ).pack(anchor="w", pady=(0, 24))

        self._etiqueta_campo(panel, "ORIGEN")
        self.origen_var = tk.StringVar(value=ESTACIONES[0])
        self.combo_origen = ttk.Combobox(
            panel,
            values=ESTACIONES,
            textvariable=self.origen_var,
            state="readonly",
            style="Modern.TCombobox",
        )
        self.combo_origen.pack(fill="x", pady=(6, 14))

        self._boton(
            panel,
            "⇅  INTERCAMBIAR",
            self.intercambiar,
            CARD_2,
            TEXT,
            hover="#203552",
            height=1,
        ).pack(fill="x", pady=(0, 14))

        self._etiqueta_campo(panel, "DESTINO")
        self.destino_var = tk.StringVar(value=ESTACIONES[-1])
        self.combo_destino = ttk.Combobox(
            panel,
            values=ESTACIONES,
            textvariable=self.destino_var,
            state="readonly",
            style="Modern.TCombobox",
        )
        self.combo_destino.pack(fill="x", pady=(6, 20))

        self._boton(
            panel,
            "CALCULAR MEJOR RUTA  →",
            self.calcular_ruta,
            BLUE,
            "white",
            hover="#2563eb",
            height=2,
            bold=True,
        ).pack(fill="x")

        tk.Frame(panel, bg="#233550", height=1).pack(fill="x", pady=24)

        tk.Label(
            panel,
            text="RUTAS RAPIDAS",
            bg=PANEL,
            fg=MUTED,
            font=("Segoe UI", 9, "bold"),
        ).pack(anchor="w", pady=(0, 10))

        self._boton(
            panel,
            "Portal de Soledad  →  La Arenosa",
            lambda: self._ruta_rapida("Portal de Soledad", "La Arenosa"),
            CARD,
            "#dbeafe",
            hover="#1b3150",
        ).pack(fill="x", pady=4)

        self._boton(
            panel,
            "Pacho Galan  →  Atlantico",
            lambda: self._ruta_rapida("Pacho Galan", "Atlantico"),
            CARD,
            "#dbeafe",
            hover="#1b3150",
        ).pack(fill="x", pady=4)

        self._boton(
            panel,
            "Limpiar resultados",
            self.limpiar,
            PANEL,
            MUTED,
            hover="#172a43",
        ).pack(fill="x", pady=(18, 0))

        nota = tk.Frame(panel, bg="#0b1728", padx=12, pady=12)
        nota.pack(fill="x", side="bottom")
        tk.Label(
            nota,
            text="SIMULACION ACADEMICA",
            bg="#0b1728",
            fg=AMBER,
            font=("Segoe UI", 8, "bold"),
        ).pack(anchor="w")
        tk.Label(
            nota,
            text="Los tiempos y conexiones expresas no corresponden a datos oficiales.",
            bg="#0b1728",
            fg=MUTED,
            font=("Segoe UI", 8),
            wraplength=240,
            justify="left",
        ).pack(anchor="w", pady=(4, 0))

    def _crear_panel_mapa(self, padre: tk.Frame) -> None:
        panel = tk.Frame(padre, bg=PANEL, padx=16, pady=16)
        panel.grid(row=0, column=1, sticky="nsew", padx=(0, 14))
        panel.grid_rowconfigure(1, weight=1)
        panel.grid_columnconfigure(0, weight=1)

        superior = tk.Frame(panel, bg=PANEL)
        superior.grid(row=0, column=0, sticky="ew", pady=(0, 12))

        tk.Label(
            superior,
            text="MAPA INTELIGENTE",
            bg=PANEL,
            fg=TEXT,
            font=("Segoe UI", 13, "bold"),
        ).pack(side="left")

        self.estado_mapa = tk.Label(
            superior,
            text="Esperando consulta",
            bg="#1e293b",
            fg=MUTED,
            font=("Segoe UI", 8, "bold"),
            padx=10,
            pady=5,
        )
        self.estado_mapa.pack(side="right")

        self.canvas = tk.Canvas(
            panel,
            bg="#0a1627",
            highlightthickness=0,
            bd=0,
        )
        self.canvas.grid(row=1, column=0, sticky="nsew")
        self.canvas.bind("<Configure>", lambda _e: self._redibujar_actual())

        leyenda = tk.Frame(panel, bg=PANEL)
        leyenda.grid(row=2, column=0, sticky="ew", pady=(12, 0))
        self._leyenda(leyenda, TRACK, "Red base")
        self._leyenda(leyenda, BLUE, "Ruta seleccionada")
        self._leyenda(leyenda, CYAN, "Vehiculo animado")

    def _crear_panel_resultados(self, padre: tk.Frame) -> None:
        panel = tk.Frame(padre, bg=BG)
        panel.grid(row=0, column=2, sticky="nsew")
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(2, weight=1)

        metricas = tk.Frame(panel, bg=BG)
        metricas.grid(row=0, column=0, sticky="ew")
        for col in range(3):
            metricas.grid_columnconfigure(col, weight=1)

        self.costo_var = tk.StringVar(value="--")
        self.ucs_var = tk.StringVar(value="--")
        self.astar_var = tk.StringVar(value="--")

        self._tarjeta_metrica(metricas, 0, "TIEMPO", self.costo_var, CYAN)
        self._tarjeta_metrica(metricas, 1, "UCS", self.ucs_var, AMBER)
        self._tarjeta_metrica(metricas, 2, "A*", self.astar_var, GREEN)

        comparador = tk.Frame(panel, bg=PANEL, padx=16, pady=14)
        comparador.grid(row=1, column=0, sticky="ew", pady=(14, 14))

        tk.Label(
            comparador,
            text="EFICIENCIA DE BUSQUEDA",
            bg=PANEL,
            fg=TEXT,
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w")

        self.canvas_barras = tk.Canvas(
            comparador,
            height=70,
            bg=PANEL,
            highlightthickness=0,
        )
        self.canvas_barras.pack(fill="x", pady=(8, 0))
        self._dibujar_barras(0, 0)

        detalle_card = tk.Frame(panel, bg=PANEL, padx=16, pady=16)
        detalle_card.grid(row=2, column=0, sticky="nsew")
        detalle_card.grid_rowconfigure(2, weight=1)
        detalle_card.grid_columnconfigure(0, weight=1)

        tk.Label(
            detalle_card,
            text="DETALLE DE LA RUTA",
            bg=PANEL,
            fg=TEXT,
            font=("Segoe UI", 12, "bold"),
        ).grid(row=0, column=0, sticky="w")

        self.resumen_var = tk.StringVar(value="Selecciona una ruta para comenzar")
        tk.Label(
            detalle_card,
            textvariable=self.resumen_var,
            bg=PANEL,
            fg=MUTED,
            font=("Segoe UI", 9),
            wraplength=310,
            justify="left",
        ).grid(row=1, column=0, sticky="ew", pady=(5, 12))

        self.detalle = tk.Text(
            detalle_card,
            bg="#0a1627",
            fg="#dbeafe",
            insertbackground="white",
            relief="flat",
            wrap="word",
            font=("Consolas", 9),
            padx=12,
            pady=12,
            spacing1=3,
            spacing3=3,
        )
        self.detalle.grid(row=2, column=0, sticky="nsew")
        self.detalle.configure(state="disabled")

    def _etiqueta_campo(self, padre: tk.Widget, texto: str) -> None:
        tk.Label(
            padre,
            text=texto,
            bg=PANEL,
            fg=MUTED,
            font=("Segoe UI", 8, "bold"),
        ).pack(anchor="w")

    def _boton(
        self,
        padre: tk.Widget,
        texto: str,
        comando,
        fondo: str,
        frente: str,
        hover: str,
        height: int = 1,
        bold: bool = False,
    ) -> tk.Button:
        boton = tk.Button(
            padre,
            text=texto,
            command=comando,
            bg=fondo,
            fg=frente,
            activebackground=hover,
            activeforeground=frente,
            relief="flat",
            bd=0,
            cursor="hand2",
            height=height,
            font=("Segoe UI", 9, "bold" if bold else "normal"),
            padx=10,
            pady=7,
        )
        boton.bind("<Enter>", lambda _e: boton.configure(bg=hover))
        boton.bind("<Leave>", lambda _e: boton.configure(bg=fondo))
        return boton

    def _leyenda(self, padre: tk.Frame, color: str, texto: str) -> None:
        bloque = tk.Frame(padre, bg=PANEL)
        bloque.pack(side="left", padx=(0, 14))
        tk.Canvas(
            bloque,
            width=10,
            height=10,
            bg=PANEL,
            highlightthickness=0,
        ).pack(side="left")
        indicador = bloque.winfo_children()[0]
        indicador.create_oval(2, 2, 8, 8, fill=color, outline="")
        tk.Label(
            bloque,
            text=texto,
            bg=PANEL,
            fg=MUTED,
            font=("Segoe UI", 8),
        ).pack(side="left", padx=(4, 0))

    def _tarjeta_metrica(
        self,
        padre: tk.Frame,
        columna: int,
        titulo: str,
        variable: tk.StringVar,
        color: str,
    ) -> None:
        card = tk.Frame(padre, bg=PANEL, padx=10, pady=12)
        card.grid(row=0, column=columna, sticky="ew", padx=(0 if columna == 0 else 5, 0))
        tk.Label(
            card,
            text=titulo,
            bg=PANEL,
            fg=MUTED,
            font=("Segoe UI", 8, "bold"),
        ).pack()
        tk.Label(
            card,
            textvariable=variable,
            bg=PANEL,
            fg=color,
            font=("Segoe UI", 17, "bold"),
        ).pack(pady=(3, 0))

    def intercambiar(self) -> None:
        origen = self.origen_var.get()
        destino = self.destino_var.get()
        self.origen_var.set(destino)
        self.destino_var.set(origen)

    def _ruta_rapida(self, origen: str, destino: str) -> None:
        self.origen_var.set(origen)
        self.destino_var.set(destino)
        self.calcular_ruta()

    def calcular_ruta(self) -> None:
        origen = self.origen_var.get()
        destino = self.destino_var.get()
        self.animacion_id += 1

        if origen == destino:
            self.ruta_actual = [origen]
            self.costo_var.set("0 min")
            self.ucs_var.set("0")
            self.astar_var.set("0")
            self.resumen_var.set("El origen y el destino corresponden a la misma estacion.")
            self.estado_mapa.configure(text="Ruta trivial", fg=AMBER)
            self._mostrar_texto(
                f"ORIGEN\n{origen}\n\nDESTINO\n{destino}\n\nCosto total: 0 minutos."
            )
            self._dibujar_barras(0, 0)
            self._redibujar_actual()
            return

        try:
            ruta_u, costo_u, expandidos_u = costo_uniforme(self.grafo, origen, destino)
            ruta_a, costo_a, expandidos_a = a_estrella(self.grafo, origen, destino)
        except ValueError as error:
            messagebox.showerror("No fue posible calcular la ruta", str(error))
            return

        self.ruta_actual = ruta_a
        self.costo_var.set(f"{costo_a} min")
        self.ucs_var.set(str(expandidos_u))
        self.astar_var.set(str(expandidos_a))

        if costo_a == costo_u:
            self.resumen_var.set(
                f"Ambos algoritmos encontraron el mismo costo minimo: {costo_a} minutos."
            )
        else:
            self.resumen_var.set("Los algoritmos devolvieron costos diferentes.")

        if expandidos_a < expandidos_u:
            comparacion = "A* fue mas eficiente al expandir menos nodos."
        elif expandidos_a == expandidos_u:
            comparacion = "Ambos algoritmos expandieron la misma cantidad de nodos."
        else:
            comparacion = "En esta consulta A* no redujo los nodos expandidos."

        lineas = [
            "RUTA SOLICITADA",
            f"Origen:  {origen}",
            f"Destino: {destino}",
            "",
            "MEJOR RUTA ENCONTRADA",
            "  →  ".join(ruta_a),
            "",
            f"Costo estimado: {costo_a} minutos",
            "",
            "TRAMOS",
        ]

        for inicio, fin, costo, tipo in detalle_tramos(self.grafo, ruta_a):
            etiqueta = "corriente" if tipo == "corriente" else "expreso simulado"
            lineas.append(f"• {inicio} → {fin}\n  {costo} min | {etiqueta}")

        lineas.extend(
            [
                "",
                "COMPARACION DE ALGORITMOS",
                f"Costo uniforme: {expandidos_u} nodos",
                f"A*: {expandidos_a} nodos",
                comparacion,
            ]
        )

        self._mostrar_texto("\n".join(lineas))
        self._dibujar_barras(expandidos_u, expandidos_a)
        self.estado_mapa.configure(text="Animando mejor ruta", fg=GREEN)
        self._redibujar_actual(animar=True)

    def _mostrar_texto(self, texto: str) -> None:
        self.detalle.configure(state="normal")
        self.detalle.delete("1.0", "end")
        self.detalle.insert("1.0", texto)
        self.detalle.configure(state="disabled")

    def limpiar(self) -> None:
        self.animacion_id += 1
        self.ruta_actual = []
        self.puntos_ruta = []
        self.costo_var.set("--")
        self.ucs_var.set("--")
        self.astar_var.set("--")
        self.resumen_var.set("Selecciona una ruta para comenzar")
        self.estado_mapa.configure(text="Esperando consulta", fg=MUTED)
        self._mostrar_texto("")
        self._dibujar_barras(0, 0)
        self._dibujar_red_base()

    def _coordenadas(self) -> dict[str, tuple[int, int]]:
        ancho = max(self.canvas.winfo_width(), 560)
        alto = max(self.canvas.winfo_height(), 500)

        margen_x = 55
        x1 = margen_x
        x2 = ancho - margen_x
        y1 = 80
        y2 = alto // 2
        y3 = alto - 80

        top = [
            (x1, y1),
            (x1 + (x2 - x1) * 0.25, y1),
            (x1 + (x2 - x1) * 0.50, y1),
            (x1 + (x2 - x1) * 0.75, y1),
            (x2, y1),
        ]
        middle = [(x2, y2), (x2 * 0.73, y2), (x2 * 0.47, y2)]
        bottom = [(x2 * 0.47, y3), (x2 * 0.27, y3), (x1, y3)]
        puntos = top + middle + bottom
        return {estacion: (int(x), int(y)) for estacion, (x, y) in zip(ESTACIONES, puntos)}

    def _dibujar_red_base(self) -> None:
        self.canvas.delete("all")
        coords = self._coordenadas()

        self.canvas.create_text(
            20,
            22,
            text="TRONCAL MURILLO · MODELO ACADEMICO",
            anchor="w",
            fill="#64748b",
            font=("Segoe UI", 8, "bold"),
        )

        for i in range(len(ESTACIONES) - 1):
            a = coords[ESTACIONES[i]]
            b = coords[ESTACIONES[i + 1]]
            self.canvas.create_line(*a, *b, fill=TRACK, width=5, capstyle="round")

        for estacion in ESTACIONES:
            x, y = coords[estacion]
            self._dibujar_estacion(estacion, x, y, activa=False)

    def _redibujar_actual(self, animar: bool = False) -> None:
        if not self.canvas.winfo_exists():
            return
        self._dibujar_red_base()
        if not self.ruta_actual:
            return

        coords = self._coordenadas()
        self.puntos_ruta = [coords[e] for e in self.ruta_actual]

        if len(self.ruta_actual) == 1:
            e = self.ruta_actual[0]
            x, y = coords[e]
            self._dibujar_estacion(e, x, y, activa=True)
            return

        if animar:
            token = self.animacion_id
            self._animar_segmentos(0, token)
        else:
            for a, b in zip(self.puntos_ruta, self.puntos_ruta[1:]):
                self.canvas.create_line(*a, *b, fill=BLUE, width=7, capstyle="round")
            for e in self.ruta_actual:
                x, y = coords[e]
                self._dibujar_estacion(e, x, y, activa=True)

    def _dibujar_estacion(self, nombre: str, x: int, y: int, activa: bool) -> None:
        color = CYAN if activa else "#64748b"
        borde = "#cffafe" if activa else "#94a3b8"
        radio = 8 if activa else 6

        self.canvas.create_oval(
            x - radio - 5,
            y - radio - 5,
            x + radio + 5,
            y + radio + 5,
            fill="#0a1627",
            outline=color if activa else "",
            width=2,
        )
        self.canvas.create_oval(
            x - radio,
            y - radio,
            x + radio,
            y + radio,
            fill=color,
            outline=borde,
            width=2,
        )

        indice = ESTACIONES.index(nombre)
        dy = -28 if indice < 5 or indice in (8, 9, 10) else 28
        self.canvas.create_text(
            x,
            y + dy,
            text=nombre,
            fill=TEXT if activa else "#94a3b8",
            font=("Segoe UI", 8, "bold" if activa else "normal"),
            width=105,
            justify="center",
        )

    def _animar_segmentos(self, indice: int, token: int) -> None:
        if token != self.animacion_id:
            return

        coords = self._coordenadas()
        if indice >= len(self.ruta_actual) - 1:
            for estacion in self.ruta_actual:
                x, y = coords[estacion]
                self._dibujar_estacion(estacion, x, y, activa=True)
            self.estado_mapa.configure(text="Ruta calculada", fg=GREEN)
            self.root.after(250, lambda: self._animar_vehiculo(0, 0.0, token))
            return

        a = coords[self.ruta_actual[indice]]
        b = coords[self.ruta_actual[indice + 1]]
        self.canvas.create_line(*a, *b, fill="#1d4ed8", width=11, capstyle="round")
        self.canvas.create_line(*a, *b, fill=BLUE, width=6, capstyle="round")

        x, y = a
        self._dibujar_estacion(self.ruta_actual[indice], x, y, activa=True)
        self.root.after(170, lambda: self._animar_segmentos(indice + 1, token))

    def _animar_vehiculo(self, tramo: int, progreso: float, token: int) -> None:
        if token != self.animacion_id or len(self.puntos_ruta) < 2:
            return

        if tramo >= len(self.puntos_ruta) - 1:
            tramo = 0
            progreso = 0.0

        a = self.puntos_ruta[tramo]
        b = self.puntos_ruta[tramo + 1]
        x = a[0] + (b[0] - a[0]) * progreso
        y = a[1] + (b[1] - a[1]) * progreso

        if self.vehiculo is not None:
            self.canvas.delete(self.vehiculo)

        self.vehiculo = self.canvas.create_oval(
            x - 7,
            y - 7,
            x + 7,
            y + 7,
            fill=CYAN,
            outline="white",
            width=2,
        )

        progreso += 0.04
        if progreso >= 1.0:
            tramo += 1
            progreso = 0.0

        self.root.after(35, lambda: self._animar_vehiculo(tramo, progreso, token))

    def _dibujar_barras(self, ucs: int, astar: int) -> None:
        self.canvas_barras.delete("all")
        ancho = max(self.canvas_barras.winfo_width(), 300)
        maximo = max(ucs, astar, 1)
        disponible = ancho - 95

        datos = [("UCS", ucs, AMBER, 20), ("A*", astar, GREEN, 50)]
        for nombre, valor, color, y in datos:
            self.canvas_barras.create_text(
                5,
                y,
                text=nombre,
                anchor="w",
                fill=MUTED,
                font=("Segoe UI", 8, "bold"),
            )
            self.canvas_barras.create_rectangle(48, y - 6, ancho - 36, y + 6, fill="#1e293b", outline="")
            longitud = disponible * (valor / maximo) if valor else 0
            self.canvas_barras.create_rectangle(48, y - 6, 48 + longitud, y + 6, fill=color, outline="")
            self.canvas_barras.create_text(
                ancho - 8,
                y,
                text=str(valor) if valor else "--",
                anchor="e",
                fill=TEXT,
                font=("Segoe UI", 8, "bold"),
            )

    def _animar_estado(self) -> None:
        actual = self.punto_estado.itemcget(self.punto_estado_id, "fill")
        nuevo = "#065f46" if actual == GREEN else GREEN
        self.punto_estado.itemconfigure(self.punto_estado_id, fill=nuevo)
        self.root.after(700, self._animar_estado)


def main() -> None:
    root = tk.Tk()
    AplicacionRutas(root)
    root.mainloop()


if __name__ == "__main__":
    main()
