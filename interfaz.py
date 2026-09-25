"""Interfaz grafica del sistema inteligente de rutas de Transmetro.

La interfaz utiliza Tkinter, incluido en la instalacion estandar de Python.
Permite seleccionar origen y destino, ejecutar costo uniforme y A*, comparar
resultados y visualizar de forma esquematica la ruta encontrada.
"""

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

        self.root.title("Sistema inteligente de rutas - Transmetro")
        self.root.geometry("1180x760")
        self.root.minsize(1050, 690)
        self.root.configure(bg="#eef2f7")

        self._configurar_estilos()
        self._crear_interfaz()
        self._dibujar_corredor([])

    def _configurar_estilos(self) -> None:
        estilo = ttk.Style()
        try:
            estilo.theme_use("clam")
        except tk.TclError:
            pass

        estilo.configure("TFrame", background="#eef2f7")
        estilo.configure("Card.TFrame", background="#ffffff")
        estilo.configure(
            "Title.TLabel",
            background="#0f2747",
            foreground="#ffffff",
            font=("Segoe UI", 20, "bold"),
        )
        estilo.configure(
            "Subtitle.TLabel",
            background="#0f2747",
            foreground="#dce8f6",
            font=("Segoe UI", 10),
        )
        estilo.configure(
            "Section.TLabel",
            background="#ffffff",
            foreground="#183153",
            font=("Segoe UI", 12, "bold"),
        )
        estilo.configure(
            "Body.TLabel",
            background="#ffffff",
            foreground="#334155",
            font=("Segoe UI", 10),
        )
        estilo.configure(
            "Metric.TLabel",
            background="#ffffff",
            foreground="#0f2747",
            font=("Segoe UI", 15, "bold"),
        )
        estilo.configure(
            "Primary.TButton",
            font=("Segoe UI", 11, "bold"),
            padding=(18, 10),
        )
        estilo.configure("TCombobox", padding=6, font=("Segoe UI", 10))

    def _crear_interfaz(self) -> None:
        encabezado = tk.Frame(self.root, bg="#0f2747", height=105)
        encabezado.pack(fill="x")
        encabezado.pack_propagate(False)

        bloque_titulo = tk.Frame(encabezado, bg="#0f2747")
        bloque_titulo.pack(fill="both", expand=True, padx=34, pady=18)

        ttk.Label(
            bloque_titulo,
            text="SISTEMA INTELIGENTE DE RUTAS - TRANSMETRO",
            style="Title.TLabel",
        ).pack(anchor="w")
        ttk.Label(
            bloque_titulo,
            text=(
                "Modelo academico de la Troncal Murillo | "
                "Busqueda de costo uniforme y algoritmo A*"
            ),
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(5, 0))

        contenedor = ttk.Frame(self.root)
        contenedor.pack(fill="both", expand=True, padx=24, pady=20)
        contenedor.columnconfigure(0, weight=0)
        contenedor.columnconfigure(1, weight=1)
        contenedor.rowconfigure(0, weight=1)

        self._crear_panel_control(contenedor)
        self._crear_panel_resultados(contenedor)

    def _crear_panel_control(self, padre: ttk.Frame) -> None:
        panel = ttk.Frame(padre, style="Card.TFrame", padding=22)
        panel.grid(row=0, column=0, sticky="ns", padx=(0, 16))
        panel.configure(width=320)
        panel.grid_propagate(False)

        ttk.Label(panel, text="Planificar ruta", style="Section.TLabel").pack(anchor="w")
        ttk.Label(
            panel,
            text="Seleccione una estacion de origen y una de destino.",
            style="Body.TLabel",
            wraplength=270,
            justify="left",
        ).pack(anchor="w", pady=(6, 20))

        ttk.Label(panel, text="Origen", style="Body.TLabel").pack(anchor="w")
        self.origen_var = tk.StringVar(value=ESTACIONES[0])
        self.combo_origen = ttk.Combobox(
            panel,
            textvariable=self.origen_var,
            values=ESTACIONES,
            state="readonly",
            width=30,
        )
        self.combo_origen.pack(fill="x", pady=(6, 16))

        ttk.Label(panel, text="Destino", style="Body.TLabel").pack(anchor="w")
        self.destino_var = tk.StringVar(value=ESTACIONES[-1])
        self.combo_destino = ttk.Combobox(
            panel,
            textvariable=self.destino_var,
            values=ESTACIONES,
            state="readonly",
            width=30,
        )
        self.combo_destino.pack(fill="x", pady=(6, 22))

        ttk.Button(
            panel,
            text="CALCULAR MEJOR RUTA",
            style="Primary.TButton",
            command=self.calcular_ruta,
        ).pack(fill="x")

        ttk.Button(
            panel,
            text="Limpiar resultados",
            command=self.limpiar,
        ).pack(fill="x", pady=(10, 0))

        separador = ttk.Separator(panel, orient="horizontal")
        separador.pack(fill="x", pady=24)

        ttk.Label(panel, text="Como funciona", style="Section.TLabel").pack(anchor="w")
        ttk.Label(
            panel,
            text=(
                "El sistema consulta una base de conocimiento formada por reglas de "
                "conexion entre estaciones. Luego calcula la ruta con costo uniforme "
                "y con A*, y compara la cantidad de nodos expandidos."
            ),
            style="Body.TLabel",
            wraplength=270,
            justify="left",
        ).pack(anchor="w", pady=(7, 0))

        ttk.Label(
            panel,
            text=(
                "Nota: los tiempos y conexiones expresas son simulados para fines "
                "academicos; no representan tiempos oficiales de Transmetro."
            ),
            style="Body.TLabel",
            wraplength=270,
            justify="left",
        ).pack(anchor="w", pady=(22, 0))

    def _crear_panel_resultados(self, padre: ttk.Frame) -> None:
        panel = ttk.Frame(padre)
        panel.grid(row=0, column=1, sticky="nsew")
        panel.columnconfigure(0, weight=1)
        panel.rowconfigure(2, weight=1)

        resumen = ttk.Frame(panel, style="Card.TFrame", padding=18)
        resumen.grid(row=0, column=0, sticky="ew")
        for columna in range(3):
            resumen.columnconfigure(columna, weight=1)

        self.costo_var = tk.StringVar(value="--")
        self.ucs_var = tk.StringVar(value="--")
        self.astar_var = tk.StringVar(value="--")

        self._crear_metrica(resumen, 0, "Costo estimado", self.costo_var)
        self._crear_metrica(resumen, 1, "Nodos - costo uniforme", self.ucs_var)
        self._crear_metrica(resumen, 2, "Nodos - A*", self.astar_var)

        self.estado_var = tk.StringVar(value="Seleccione origen y destino para comenzar.")
        ttk.Label(
            panel,
            textvariable=self.estado_var,
            background="#eef2f7",
            foreground="#475569",
            font=("Segoe UI", 10),
        ).grid(row=1, column=0, sticky="ew", pady=(10, 10))

        cuerpo = ttk.Frame(panel)
        cuerpo.grid(row=2, column=0, sticky="nsew")
        cuerpo.columnconfigure(0, weight=1)
        cuerpo.columnconfigure(1, weight=1)
        cuerpo.rowconfigure(0, weight=1)

        mapa_card = ttk.Frame(cuerpo, style="Card.TFrame", padding=14)
        mapa_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        mapa_card.rowconfigure(1, weight=1)
        mapa_card.columnconfigure(0, weight=1)

        ttk.Label(mapa_card, text="Esquema de la ruta", style="Section.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 8)
        )

        self.canvas = tk.Canvas(
            mapa_card,
            bg="#ffffff",
            highlightthickness=0,
            width=430,
            height=510,
        )
        self.canvas.grid(row=1, column=0, sticky="nsew")

        detalle_card = ttk.Frame(cuerpo, style="Card.TFrame", padding=14)
        detalle_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        detalle_card.rowconfigure(1, weight=1)
        detalle_card.columnconfigure(0, weight=1)

        ttk.Label(detalle_card, text="Detalle del resultado", style="Section.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 8)
        )

        self.detalle = ScrolledText(
            detalle_card,
            wrap="word",
            font=("Consolas", 9),
            relief="flat",
            bg="#f8fafc",
            fg="#1e293b",
            padx=12,
            pady=12,
        )
        self.detalle.grid(row=1, column=0, sticky="nsew")
        self.detalle.insert(
            "1.0",
            "Aqui se mostraran la ruta, los tramos, el costo y la comparacion entre algoritmos.",
        )
        self.detalle.configure(state="disabled")

    def _crear_metrica(
        self,
        padre: ttk.Frame,
        columna: int,
        titulo: str,
        variable: tk.StringVar,
    ) -> None:
        bloque = ttk.Frame(padre, style="Card.TFrame")
        bloque.grid(row=0, column=columna, sticky="ew", padx=10)
        ttk.Label(bloque, text=titulo, style="Body.TLabel").pack(anchor="center")
        ttk.Label(bloque, textvariable=variable, style="Metric.TLabel").pack(
            anchor="center", pady=(5, 0)
        )

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
            self.estado_var.set("El origen y el destino son la misma estacion.")
            self._mostrar_detalle_mismo_punto(origen)
            self._dibujar_corredor(self.ruta_actual)
            return

        try:
            resultado_ucs = costo_uniforme(self.grafo, origen, destino)
            resultado_astar = a_estrella(self.grafo, origen, destino)
        except ValueError as error:
            messagebox.showerror("No fue posible calcular la ruta", str(error))
            return

        ruta_u, costo_u, expandidos_u = resultado_ucs
        ruta_a, costo_a, expandidos_a = resultado_astar

        self.ruta_actual = ruta_a
        self.costo_var.set(f"{costo_a} min")
        self.ucs_var.set(str(expandidos_u))
        self.astar_var.set(str(expandidos_a))

        if expandidos_a < expandidos_u:
            comparacion = "A* expandio menos nodos gracias a la heuristica."
        elif expandidos_a == expandidos_u:
            comparacion = "Ambos algoritmos expandieron la misma cantidad de nodos."
        else:
            comparacion = "En esta consulta A* no redujo los nodos expandidos."

        if costo_a == costo_u:
            estado = f"Ambos algoritmos encontraron un costo minimo de {costo_a} minutos."
        else:
            estado = "Los algoritmos devolvieron costos diferentes; revise el modelo."

        self.estado_var.set(estado)
        self._mostrar_detalle(
            origen,
            destino,
            ruta_u,
            costo_u,
            expandidos_u,
            ruta_a,
            costo_a,
            expandidos_a,
            comparacion,
        )
        self._dibujar_corredor(ruta_a)

    def _mostrar_detalle(
        self,
        origen: str,
        destino: str,
        ruta_u: list[str],
        costo_u: int,
        expandidos_u: int,
        ruta_a: list[str],
        costo_a: int,
        expandidos_a: int,
        comparacion: str,
    ) -> None:
        lineas = [
            "RUTA SOLICITADA",
            f"Origen:  {origen}",
            f"Destino: {destino}",
            "",
            "BUSQUEDA DE COSTO UNIFORME",
            " -> ".join(ruta_u),
            f"Costo total: {costo_u} minutos",
            f"Nodos expandidos: {expandidos_u}",
            "",
            "BUSQUEDA A*",
            " -> ".join(ruta_a),
            f"Costo total: {costo_a} minutos",
            f"Nodos expandidos: {expandidos_a}",
            "",
            "TRAMOS DE LA RUTA A*",
        ]

        for inicio, fin, costo, tipo in detalle_tramos(self.grafo, ruta_a):
            etiqueta = "corriente" if tipo == "corriente" else "expreso simulado"
            lineas.append(f"- {inicio} -> {fin}: {costo} min ({etiqueta})")

        lineas.extend(["", "COMPARACION", comparacion])

        self.detalle.configure(state="normal")
        self.detalle.delete("1.0", "end")
        self.detalle.insert("1.0", "\n".join(lineas))
        self.detalle.configure(state="disabled")

    def _mostrar_detalle_mismo_punto(self, estacion: str) -> None:
        texto = (
            "RUTA SOLICITADA\n"
            f"Origen:  {estacion}\n"
            f"Destino: {estacion}\n\n"
            "El origen y el destino son la misma estacion.\n"
            "Costo total: 0 minutos."
        )
        self.detalle.configure(state="normal")
        self.detalle.delete("1.0", "end")
        self.detalle.insert("1.0", texto)
        self.detalle.configure(state="disabled")

    def _dibujar_corredor(self, ruta: list[str]) -> None:
        self.canvas.delete("all")
        ancho = max(self.canvas.winfo_width(), 420)
        alto = max(self.canvas.winfo_height(), 500)

        x = 48
        margen_superior = 28
        margen_inferior = 30
        paso = (alto - margen_superior - margen_inferior) / (len(ESTACIONES) - 1)
        posiciones = {
            estacion: (x, margen_superior + indice * paso)
            for indice, estacion in enumerate(ESTACIONES)
        }

        self.canvas.create_text(
            ancho - 12,
            12,
            text="Esquema academico (no geografico)",
            anchor="ne",
            fill="#64748b",
            font=("Segoe UI", 8),
        )

        y_inicio = posiciones[ESTACIONES[0]][1]
        y_fin = posiciones[ESTACIONES[-1]][1]
        self.canvas.create_line(x, y_inicio, x, y_fin, fill="#cbd5e1", width=4)

        if len(ruta) > 1:
            for inicio, fin in zip(ruta, ruta[1:]):
                x1, y1 = posiciones[inicio]
                x2, y2 = posiciones[fin]
                self.canvas.create_line(
                    x1,
                    y1,
                    x2,
                    y2,
                    fill="#2563eb",
                    width=6,
                    capstyle="round",
                )

        for estacion in ESTACIONES:
            px, py = posiciones[estacion]
            seleccionada = estacion in ruta
            relleno = "#2563eb" if seleccionada else "#ffffff"
            borde = "#1d4ed8" if seleccionada else "#94a3b8"
            texto = "#0f2747" if seleccionada else "#475569"

            self.canvas.create_oval(
                px - 7,
                py - 7,
                px + 7,
                py + 7,
                fill=relleno,
                outline=borde,
                width=2,
            )
            self.canvas.create_text(
                px + 18,
                py,
                text=estacion,
                anchor="w",
                fill=texto,
                font=("Segoe UI", 9, "bold" if seleccionada else "normal"),
            )

    def limpiar(self) -> None:
        self.origen_var.set(ESTACIONES[0])
        self.destino_var.set(ESTACIONES[-1])
        self.ruta_actual = []
        self.costo_var.set("--")
        self.ucs_var.set("--")
        self.astar_var.set("--")
        self.estado_var.set("Seleccione origen y destino para comenzar.")
        self.detalle.configure(state="normal")
        self.detalle.delete("1.0", "end")
        self.detalle.insert(
            "1.0",
            "Aqui se mostraran la ruta, los tramos, el costo y la comparacion entre algoritmos.",
        )
        self.detalle.configure(state="disabled")
        self._dibujar_corredor([])


def main() -> None:
    root = tk.Tk()
    AplicacionRutas(root)
    root.mainloop()


if __name__ == "__main__":
    main()
