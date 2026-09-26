"""Interfaz grafica del sistema inteligente de rutas de Transmetro.

La interfaz utiliza Tkinter, incluido en la instalacion estandar de Python.
Incluye un mapa academico estilizado con fondo urbano, trazados curvos,
animacion simple de recorrido y comparacion visual entre costo uniforme y A*.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from tkinter.scrolledtext import ScrolledText

from src.base_conocimiento import ESTACIONES, construir_grafo
from src.busqueda import a_estrella, costo_uniforme, detalle_tramos


class AplicacionRutas:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.grafo = construir_grafo()
        self.ruta_actual: list[str] = []
        self.segmentos_animacion: list[tuple[tuple[int, int], tuple[int, int]]] = []
        self.anim_index = 0
        self.anim_progress = 0.0
        self.anim_dot = None
        self.anim_after = None

        self.root.title("Sistema inteligente de rutas - Transmetro")
        self.root.geometry("1280x820")
        self.root.minsize(1160, 740)
        self.root.configure(bg="#08111f")

        self.estaciones_pos = {
            "Portal de Soledad": (70, 95),
            "Pacho Galan": (205, 118),
            "Pedro Ramaya Beltran": (350, 92),
            "Joaquin Barrios Polo": (495, 126),
            "Buenos Aires": (650, 94),
            "La Ocho": (690, 245),
            "La Catorce": (535, 300),
            "La Veintiuna": (355, 276),
            "Atlantico": (330, 455),
            "Chiquinquira": (190, 438),
            "La Arenosa": (72, 472),
        }

        self._configurar_estilos()
        self._crear_interfaz()
        self._dibujar_corredor([])

    def _configurar_estilos(self) -> None:
        estilo = ttk.Style()
        try:
            estilo.theme_use("clam")
        except tk.TclError:
            pass

        estilo.configure("TFrame", background="#08111f")
        estilo.configure("Panel.TFrame", background="#0c1728")
        estilo.configure("Card.TFrame", background="#0f1d33")
        estilo.configure("Title.TLabel", background="#08111f", foreground="#f8fafc", font=("Segoe UI", 22, "bold"))
        estilo.configure("Subtitle.TLabel", background="#08111f", foreground="#94a3b8", font=("Segoe UI", 10))
        estilo.configure("Section.TLabel", background="#0f1d33", foreground="#e2e8f0", font=("Segoe UI", 12, "bold"))
        estilo.configure("SectionDark.TLabel", background="#0c1728", foreground="#e2e8f0", font=("Segoe UI", 12, "bold"))
        estilo.configure("Body.TLabel", background="#0f1d33", foreground="#b7c4d6", font=("Segoe UI", 10))
        estilo.configure("DarkBody.TLabel", background="#0c1728", foreground="#b7c4d6", font=("Segoe UI", 10))
        estilo.configure("MetricTitle.TLabel", background="#0f1d33", foreground="#8aa3c2", font=("Segoe UI", 9, "bold"))
        estilo.configure("MetricValue.TLabel", background="#0f1d33", foreground="#f8fafc", font=("Segoe UI", 20, "bold"))
        estilo.configure("Primary.TButton", font=("Segoe UI", 11, "bold"), padding=(18, 11))
        estilo.configure("Ghost.TButton", font=("Segoe UI", 10), padding=(14, 8))
        estilo.configure("TCombobox", padding=8, font=("Segoe UI", 10))

    def _crear_interfaz(self) -> None:
        encabezado = tk.Frame(self.root, bg="#08111f", height=94)
        encabezado.pack(fill="x", padx=22, pady=(18, 10))
        encabezado.pack_propagate(False)

        ttk.Label(encabezado, text="SISTEMA INTELIGENTE DE RUTAS - TRANSMETRO", style="Title.TLabel").pack(anchor="w")
        ttk.Label(encabezado, text="Base de conocimiento, reglas logicas, costo uniforme y A* | Visualizacion academica del corredor", style="Subtitle.TLabel").pack(anchor="w", pady=(4, 0))

        contenedor = ttk.Frame(self.root)
        contenedor.pack(fill="both", expand=True, padx=22, pady=(0, 22))
        contenedor.columnconfigure(0, weight=0)
        contenedor.columnconfigure(1, weight=1)
        contenedor.rowconfigure(0, weight=1)

        self._crear_panel_control(contenedor)
        self._crear_panel_resultados(contenedor)

    def _crear_panel_control(self, padre: ttk.Frame) -> None:
        panel = ttk.Frame(padre, style="Panel.TFrame", padding=20)
        panel.grid(row=0, column=0, sticky="ns", padx=(0, 16))
        panel.configure(width=325)
        panel.grid_propagate(False)

        ttk.Label(panel, text="Planificador", style="SectionDark.TLabel").pack(anchor="w")
        ttk.Label(panel, text="Selecciona origen y destino para calcular la mejor ruta y compararla con A*.", style="DarkBody.TLabel", wraplength=270, justify="left").pack(anchor="w", pady=(6, 18))

        ttk.Label(panel, text="Estacion de origen", style="DarkBody.TLabel").pack(anchor="w")
        self.origen_var = tk.StringVar(value=ESTACIONES[0])
        ttk.Combobox(panel, textvariable=self.origen_var, values=ESTACIONES, state="readonly", width=28).pack(fill="x", pady=(6, 14))

        ttk.Label(panel, text="Estacion de destino", style="DarkBody.TLabel").pack(anchor="w")
        self.destino_var = tk.StringVar(value=ESTACIONES[-1])
        ttk.Combobox(panel, textvariable=self.destino_var, values=ESTACIONES, state="readonly", width=28).pack(fill="x", pady=(6, 18))

        ttk.Button(panel, text="CALCULAR RUTA", style="Primary.TButton", command=self.calcular_ruta).pack(fill="x")

        acciones = ttk.Frame(panel, style="Panel.TFrame")
        acciones.pack(fill="x", pady=(10, 0))
        acciones.columnconfigure(0, weight=1)
        acciones.columnconfigure(1, weight=1)
        ttk.Button(acciones, text="Ejemplo 1", style="Ghost.TButton", command=self.cargar_ejemplo_1).grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ttk.Button(acciones, text="Ejemplo 2", style="Ghost.TButton", command=self.cargar_ejemplo_2).grid(row=0, column=1, sticky="ew", padx=(6, 0))

        ttk.Button(panel, text="Limpiar resultados", style="Ghost.TButton", command=self.limpiar).pack(fill="x", pady=(10, 0))
        ttk.Separator(panel, orient="horizontal").pack(fill="x", pady=22)

        ttk.Label(panel, text="Informacion", style="SectionDark.TLabel").pack(anchor="w")
        info = (
            "• Costo uniforme prioriza el costo acumulado real.\n"
            "• A* combina costo acumulado y heuristica.\n"
            "• El mapa muestra un trazado urbano estilizado.\n"
            "• Las conexiones expresas son simuladas con fines academicos."
        )
        ttk.Label(panel, text=info, style="DarkBody.TLabel", justify="left", wraplength=275).pack(anchor="w", pady=(7, 0))

        self.estado_card = tk.Frame(panel, bg="#12233d", highlightthickness=1, highlightbackground="#1f3558")
        self.estado_card.pack(fill="x", pady=(22, 0))
        tk.Label(self.estado_card, text="ESTADO DEL SISTEMA", bg="#12233d", fg="#8fb4e8", font=("Segoe UI", 9, "bold"), anchor="w", padx=14, pady=10).pack(fill="x")
        self.estado_var = tk.StringVar(value="Listo para calcular una ruta.")
        tk.Label(self.estado_card, textvariable=self.estado_var, bg="#12233d", fg="#e2e8f0", justify="left", wraplength=270, font=("Segoe UI", 10), anchor="w", padx=14, pady=0).pack(fill="x", pady=(0, 12))

    def _crear_panel_resultados(self, padre: ttk.Frame) -> None:
        panel = ttk.Frame(padre)
        panel.grid(row=0, column=1, sticky="nsew")
        panel.columnconfigure(0, weight=1)
        panel.rowconfigure(2, weight=1)

        metricas = ttk.Frame(panel)
        metricas.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        for i in range(4):
            metricas.columnconfigure(i, weight=1)

        self.costo_var = tk.StringVar(value="--")
        self.ucs_var = tk.StringVar(value="--")
        self.astar_var = tk.StringVar(value="--")
        self.ruta_var = tk.StringVar(value="--")

        self._crear_metrica(metricas, 0, "Costo estimado", self.costo_var)
        self._crear_metrica(metricas, 1, "Nodos UCS", self.ucs_var)
        self._crear_metrica(metricas, 2, "Nodos A*", self.astar_var)
        self._crear_metrica(metricas, 3, "Estaciones en ruta", self.ruta_var)

        comparador = ttk.Frame(panel, style="Card.TFrame", padding=14)
        comparador.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        comparador.columnconfigure(1, weight=1)
        ttk.Label(comparador, text="Comparacion visual", style="Section.TLabel").grid(row=0, column=0, sticky="w")

        self.comp_texto = tk.StringVar(value="Todavia no hay comparacion disponible.")
        ttk.Label(comparador, textvariable=self.comp_texto, style="Body.TLabel").grid(row=0, column=1, sticky="e")

        self.canvas_comp = tk.Canvas(comparador, height=72, bg="#0f1d33", highlightthickness=0)
        self.canvas_comp.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(10, 0))

        cuerpo = ttk.Frame(panel)
        cuerpo.grid(row=2, column=0, sticky="nsew")
        cuerpo.columnconfigure(0, weight=3)
        cuerpo.columnconfigure(1, weight=2)
        cuerpo.rowconfigure(0, weight=1)

        mapa_card = ttk.Frame(cuerpo, style="Card.TFrame", padding=12)
        mapa_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        mapa_card.rowconfigure(1, weight=1)
        mapa_card.columnconfigure(0, weight=1)

        cab = ttk.Frame(mapa_card, style="Card.TFrame")
        cab.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        cab.columnconfigure(0, weight=1)
        ttk.Label(cab, text="MAPA INTELIGENTE", style="Section.TLabel").grid(row=0, column=0, sticky="w")
        self.badge_var = tk.StringVar(value="Sin ruta")
        tk.Label(cab, textvariable=self.badge_var, bg="#15304f", fg="#7df9b6", font=("Segoe UI", 9, "bold"), padx=12, pady=6).grid(row=0, column=1, sticky="e")

        self.canvas = tk.Canvas(mapa_card, bg="#051225", highlightthickness=0, width=700, height=560)
        self.canvas.grid(row=1, column=0, sticky="nsew")

        detalle_card = ttk.Frame(cuerpo, style="Card.TFrame", padding=12)
        detalle_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        detalle_card.rowconfigure(1, weight=1)
        detalle_card.columnconfigure(0, weight=1)
        ttk.Label(detalle_card, text="Detalle de la ruta", style="Section.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 8))

        self.detalle = ScrolledText(detalle_card, wrap="word", font=("Consolas", 10), relief="flat", bg="#0a1629", fg="#dde7f2", insertbackground="#dde7f2", padx=12, pady=12)
        self.detalle.grid(row=1, column=0, sticky="nsew")
        self.detalle.insert("1.0", "Aqui se mostraran la ruta, los costos, los tramos y la comparacion entre algoritmos.")
        self.detalle.configure(state="disabled")

    def _crear_metrica(self, padre: ttk.Frame, columna: int, titulo: str, variable: tk.StringVar) -> None:
        card = ttk.Frame(padre, style="Card.TFrame", padding=14)
        card.grid(row=0, column=columna, sticky="ew", padx=(0 if columna == 0 else 8, 0))
        ttk.Label(card, text=titulo, style="MetricTitle.TLabel").pack(anchor="w")
        ttk.Label(card, textvariable=variable, style="MetricValue.TLabel").pack(anchor="w", pady=(6, 0))

    def cargar_ejemplo_1(self) -> None:
        self.origen_var.set("Portal de Soledad")
        self.destino_var.set("La Arenosa")
        self.calcular_ruta()

    def cargar_ejemplo_2(self) -> None:
        self.origen_var.set("Pacho Galan")
        self.destino_var.set("Atlantico")
        self.calcular_ruta()

    def calcular_ruta(self) -> None:
        origen = self.origen_var.get()
        destino = self.destino_var.get()

        if not origen or not destino:
            messagebox.showwarning("Datos incompletos", "Seleccione origen y destino.")
            return

        if origen == destino:
            self.ruta_actual = [origen]
            self.costo_var.set("0 min")
            self.ucs_var.set("0")
            self.astar_var.set("0")
            self.ruta_var.set("1")
            self.comp_texto.set("No se requiere comparacion: origen y destino coinciden.")
            self.estado_var.set("El origen y el destino son la misma estacion.")
            self.badge_var.set("Ruta trivial")
            self._mostrar_detalle_mismo_punto(origen)
            self._dibujar_barras(0, 0)
            self._dibujar_corredor(self.ruta_actual)
            return

        try:
            resultado_ucs = costo_uniforme(self.grafo, origen, destino)
            resultado_astar = a_estrella(self.grafo, origen, destino)
        except ValueError as error:
            messagebox.showerror("No fue posible calcular la ruta", str(error))
            return

        ruta_u, costo_u, exp_u = resultado_ucs
        ruta_a, costo_a, exp_a = resultado_astar

        self.ruta_actual = ruta_a
        self.costo_var.set(f"{costo_a} min")
        self.ucs_var.set(str(exp_u))
        self.astar_var.set(str(exp_a))
        self.ruta_var.set(str(len(ruta_a)))
        self.badge_var.set("Ruta calculada")

        if exp_a < exp_u:
            comparacion = "A* expandio menos nodos gracias a la heuristica."
        elif exp_a == exp_u:
            comparacion = "Ambos algoritmos expandieron la misma cantidad de nodos."
        else:
            comparacion = "En esta consulta A* no redujo los nodos expandidos."

        self.comp_texto.set(comparacion)
        self.estado_var.set(f"Ruta calculada de {origen} a {destino}. Costo minimo encontrado: {costo_a} min.")
        self._mostrar_detalle(origen, destino, ruta_u, costo_u, exp_u, ruta_a, costo_a, exp_a, comparacion)
        self._dibujar_barras(exp_u, exp_a)
        self._dibujar_corredor(ruta_a)

    def _mostrar_detalle(self, origen: str, destino: str, ruta_u: list[str], costo_u: int, exp_u: int, ruta_a: list[str], costo_a: int, exp_a: int, comparacion: str) -> None:
        texto = [
            "RUTA SOLICITADA",
            f"Origen : {origen}",
            f"Destino: {destino}",
            "",
            "BUSQUEDA DE COSTO UNIFORME",
            " -> ".join(ruta_u),
            f"Costo total     : {costo_u} minutos",
            f"Nodos expandidos: {exp_u}",
            "",
            "BUSQUEDA A*",
            " -> ".join(ruta_a),
            f"Costo total     : {costo_a} minutos",
            f"Nodos expandidos: {exp_a}",
            "",
            "TRAMOS DE LA RUTA A*",
        ]
        for inicio, fin, costo, tipo in detalle_tramos(self.grafo, ruta_a):
            etiqueta = "corriente" if tipo == "corriente" else "expreso simulado"
            texto.append(f"- {inicio} -> {fin}: {costo} min ({etiqueta})")
        texto.extend(["", "COMPARACION", comparacion])

        self.detalle.configure(state="normal")
        self.detalle.delete("1.0", "end")
        self.detalle.insert("1.0", "\n".join(texto))
        self.detalle.configure(state="disabled")

    def _mostrar_detalle_mismo_punto(self, estacion: str) -> None:
        texto = f"RUTA SOLICITADA\nOrigen : {estacion}\nDestino: {estacion}\n\nEl origen y el destino son la misma estacion.\nCosto total: 0 minutos."
        self.detalle.configure(state="normal")
        self.detalle.delete("1.0", "end")
        self.detalle.insert("1.0", texto)
        self.detalle.configure(state="disabled")

    def limpiar(self) -> None:
        if self.anim_after is not None:
            self.root.after_cancel(self.anim_after)
            self.anim_after = None
        self.ruta_actual = []
        self.costo_var.set("--")
        self.ucs_var.set("--")
        self.astar_var.set("--")
        self.ruta_var.set("--")
        self.estado_var.set("Listo para calcular una ruta.")
        self.comp_texto.set("Todavia no hay comparacion disponible.")
        self.badge_var.set("Sin ruta")
        self.detalle.configure(state="normal")
        self.detalle.delete("1.0", "end")
        self.detalle.insert("1.0", "Aqui se mostraran la ruta, los costos, los tramos y la comparacion entre algoritmos.")
        self.detalle.configure(state="disabled")
        self._dibujar_barras(0, 0)
        self._dibujar_corredor([])

    def _dibujar_barras(self, ucs: int, astar: int) -> None:
        c = self.canvas_comp
        c.delete("all")
        w = max(c.winfo_width(), 300)
        max_v = max(ucs, astar, 1)
        left = 110
        right = w - 40
        usable = max(60, right - left)
        base_y1 = 24
        base_y2 = 50
        c.create_text(18, base_y1 + 7, text="UCS", fill="#c7d2e2", anchor="w", font=("Segoe UI", 9, "bold"))
        c.create_text(18, base_y2 + 7, text="A*", fill="#c7d2e2", anchor="w", font=("Segoe UI", 9, "bold"))
        c.create_rectangle(left, base_y1, right, base_y1 + 14, fill="#1a2b46", outline="")
        c.create_rectangle(left, base_y2, right, base_y2 + 14, fill="#1a2b46", outline="")
        if ucs:
            c.create_rectangle(left, base_y1, left + usable * (ucs / max_v), base_y1 + 14, fill="#5b8cff", outline="")
        if astar:
            c.create_rectangle(left, base_y2, left + usable * (astar / max_v), base_y2 + 14, fill="#33d1ff", outline="")
        c.create_text(right + 8, base_y1 + 7, text=str(ucs), fill="#e2e8f0", anchor="w", font=("Segoe UI", 9, "bold"))
        c.create_text(right + 8, base_y2 + 7, text=str(astar), fill="#e2e8f0", anchor="w", font=("Segoe UI", 9, "bold"))

    def _dibujar_corredor(self, ruta: list[str]) -> None:
        if self.anim_after is not None:
            self.root.after_cancel(self.anim_after)
            self.anim_after = None
        self.canvas.delete("all")
        self._dibujar_fondo_ciudad()
        self._dibujar_calles_contexto()
        self._dibujar_red_base()
        self._dibujar_ruta(ruta)
        self._dibujar_estaciones(ruta)
        self._preparar_animacion(ruta)

    def _dibujar_fondo_ciudad(self) -> None:
        c = self.canvas
        w = max(c.winfo_width(), 700)
        h = max(c.winfo_height(), 560)
        c.create_rectangle(0, 0, w, h, fill="#051225", outline="")
        for i, color in enumerate(["#06152a", "#07172d", "#081a31"]):
            m = 16 + i * 18
            c.create_rectangle(m, m, w - m, h - m, outline=color)
        c.create_text(18, 18, text="TRONCAL MURILLO · MODELO ACADEMICO", fill="#7590b4", anchor="nw", font=("Segoe UI", 10, "bold"))

    def _dibujar_calles_contexto(self) -> None:
        c = self.canvas
        color = "#0e2a45"
        color2 = "#0b2239"
        horizontales = [72, 138, 205, 272, 338, 405, 472, 535]
        for y in horizontales:
            pts = [16, y, 120, y + 6, 230, y - 5, 345, y + 7, 465, y - 6, 585, y + 5, 705, y]
            c.create_line(*pts, fill=color, width=2, smooth=True)
        verticales = [88, 175, 265, 355, 445, 535, 625, 705]
        for x in verticales:
            pts = [x, 38, x - 6, 135, x + 8, 235, x - 5, 335, x + 7, 445, x, 545]
            c.create_line(*pts, fill=color2, width=2, smooth=True)
        c.create_line(25, 500, 145, 455, 270, 405, 390, 345, 525, 255, 710, 155, fill="#12304d", width=2, smooth=True)
        c.create_line(35, 175, 150, 195, 275, 225, 410, 255, 555, 300, 715, 330, fill="#102a44", width=2, smooth=True)

    def _dibujar_red_base(self) -> None:
        base_edges = [
            ("Portal de Soledad", "Pacho Galan"),
            ("Pacho Galan", "Pedro Ramaya Beltran"),
            ("Pedro Ramaya Beltran", "Joaquin Barrios Polo"),
            ("Joaquin Barrios Polo", "Buenos Aires"),
            ("Buenos Aires", "La Ocho"),
            ("La Ocho", "La Catorce"),
            ("La Catorce", "La Veintiuna"),
            ("La Veintiuna", "Atlantico"),
            ("Atlantico", "Chiquinquira"),
            ("Chiquinquira", "La Arenosa"),
        ]
        for a, b in base_edges:
            self._draw_soft_connection(self.estaciones_pos[a], self.estaciones_pos[b], "#314863", 4)

    def _dibujar_ruta(self, ruta: list[str]) -> None:
        if len(ruta) < 2:
            return
        for a, b in zip(ruta, ruta[1:]):
            self._draw_soft_connection(self.estaciones_pos[a], self.estaciones_pos[b], "#5b8cff", 8, glow=True)

    def _draw_soft_connection(self, p1, p2, color, width, glow=False):
        c = self.canvas
        x1, y1 = p1
        x2, y2 = p2
        dx = x2 - x1
        dy = y2 - y1
        dist = max((dx * dx + dy * dy) ** 0.5, 1)
        nx = -dy / dist
        ny = dx / dist
        bend = min(46, dist * 0.14)
        cx = (x1 + x2) / 2 + nx * bend
        cy = (y1 + y2) / 2 + ny * bend
        pts = [x1, y1, cx, cy, x2, y2]
        if glow:
            c.create_line(*pts, fill="#183a7c", width=width + 6, smooth=True)
            c.create_line(*pts, fill="#2b62d8", width=width + 2, smooth=True)
        c.create_line(*pts, fill=color, width=width, smooth=True)

    def _dibujar_estaciones(self, ruta: list[str]) -> None:
        c = self.canvas
        ruta_set = set(ruta)
        for nombre, (x, y) in self.estaciones_pos.items():
            en_ruta = nombre in ruta_set
            radio = 12 if en_ruta else 7
            borde = "#5ae3ff" if en_ruta else "#9fb4cf"
            relleno = "#103b6d" if en_ruta else "#617791"
            if en_ruta:
                c.create_oval(x - 15, y - 15, x + 15, y + 15, outline="#5ae3ff", width=2)
            c.create_oval(x - radio, y - radio, x + radio, y + radio, fill=relleno, outline=borde, width=2)
            fill = "#ffffff" if en_ruta else "#b9c8da"
            anchor = "s" if y < 160 else "n"
            offset = -18 if anchor == "s" else 18
            maxw = 140 if len(nombre) > 15 else 110
            c.create_text(x, y + offset, text=nombre, fill=fill, width=maxw, font=("Segoe UI", 10 if en_ruta else 9, "bold" if en_ruta else "normal"), anchor=anchor)

    def _preparar_animacion(self, ruta: list[str]) -> None:
        self.segmentos_animacion = []
        self.anim_index = 0
        self.anim_progress = 0.0
        if len(ruta) < 2:
            return
        for a, b in zip(ruta, ruta[1:]):
            self.segmentos_animacion.append((self.estaciones_pos[a], self.estaciones_pos[b]))
        self.anim_dot = self.canvas.create_oval(0, 0, 0, 0, fill="#9effff", outline="#ffffff")
        self._animar()

    def _animar(self) -> None:
        if not self.segmentos_animacion:
            return
        (x1, y1), (x2, y2) = self.segmentos_animacion[self.anim_index]
        dx = x2 - x1
        dy = y2 - y1
        dist = max((dx * dx + dy * dy) ** 0.5, 1)
        nx = -dy / dist
        ny = dx / dist
        bend = min(46, dist * 0.14)
        cx = (x1 + x2) / 2 + nx * bend
        cy = (y1 + y2) / 2 + ny * bend
        t = self.anim_progress
        x = (1 - t) ** 2 * x1 + 2 * (1 - t) * t * cx + t * t * x2
        y = (1 - t) ** 2 * y1 + 2 * (1 - t) * t * cy + t * t * y2
        r = 6
        self.canvas.coords(self.anim_dot, x - r, y - r, x + r, y + r)
        self.anim_progress += 0.035
        if self.anim_progress >= 1.0:
            self.anim_progress = 0.0
            self.anim_index = (self.anim_index + 1) % len(self.segmentos_animacion)
        self.anim_after = self.root.after(35, self._animar)


def main() -> None:
    root = tk.Tk()
    app = AplicacionRutas(root)
    app._dibujar_barras(0, 0)
    root.mainloop()


if __name__ == "__main__":
    main()
