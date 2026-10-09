"""Modelo supervisado con arbol de decision implementado solo con Python estandar.

Esta version evita dependencias binarias externas para que el proyecto pueda ejecutarse
en equipos donde Windows Application Control bloquea extensiones compiladas.
"""

from __future__ import annotations

import csv
import html
import random
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any


BASE = Path(__file__).resolve().parents[1]
DATASET = BASE / "data" / "datos_transmetro_supervisado.csv"
RESULTADOS = BASE / "resultados"

FEATURES = [
    "origen", "destino", "numero_paradas", "hora", "hora_pico",
    "tipo_dia", "pasajeros", "lluvia", "incidente", "tiempo_base_min",
]
OBJETIVO = "estado_servicio"
CATEGORICAS = {"origen", "destino", "tipo_dia"}
NUMERICAS = set(FEATURES) - CATEGORICAS
CLASES = ["Normal", "Demorado", "Critico"]


@dataclass
class Nodo:
    prediccion: str
    profundidad: int
    conteos: dict[str, int]
    variable: str | None = None
    valor: Any = None
    categorica: bool = False
    izquierda: "Nodo | None" = None
    derecha: "Nodo | None" = None


def cargar_dataset():
    with DATASET.open("r", encoding="utf-8", newline="") as archivo:
        filas = list(csv.DictReader(archivo))

    for fila in filas:
        for campo in NUMERICAS:
            fila[campo] = float(fila[campo])
        fila["id"] = int(fila["id"])
    return filas


def gini(filas):
    if not filas:
        return 0.0
    conteos = Counter(f[OBJETIVO] for f in filas)
    total = len(filas)
    return 1.0 - sum((cantidad / total) ** 2 for cantidad in conteos.values())


def clase_mayoritaria(filas):
    conteos = Counter(f[OBJETIVO] for f in filas)
    return max(CLASES, key=lambda clase: (conteos[clase], -CLASES.index(clase)))


def dividir(filas, variable, valor, categorica):
    if categorica:
        izquierda = [f for f in filas if f[variable] == valor]
        derecha = [f for f in filas if f[variable] != valor]
    else:
        izquierda = [f for f in filas if f[variable] <= valor]
        derecha = [f for f in filas if f[variable] > valor]
    return izquierda, derecha


def mejor_division(filas, min_muestras_hoja=4):
    impureza_inicial = gini(filas)
    mejor = None

    for variable in FEATURES:
        categorica = variable in CATEGORICAS
        valores = sorted({f[variable] for f in filas})

        if categorica:
            candidatos = valores
        else:
            candidatos = [
                (a + b) / 2
                for a, b in zip(valores, valores[1:])
            ]

        for valor in candidatos:
            izquierda, derecha = dividir(filas, variable, valor, categorica)
            if len(izquierda) < min_muestras_hoja or len(derecha) < min_muestras_hoja:
                continue

            total = len(filas)
            impureza = (
                len(izquierda) / total * gini(izquierda)
                + len(derecha) / total * gini(derecha)
            )
            ganancia = impureza_inicial - impureza

            if mejor is None or ganancia > mejor[0]:
                mejor = (ganancia, variable, valor, categorica, izquierda, derecha)

    return mejor


def construir_arbol(filas, profundidad=0, max_profundidad=5, min_muestras_hoja=4):
    nodo = Nodo(
        prediccion=clase_mayoritaria(filas),
        profundidad=profundidad,
        conteos=dict(Counter(f[OBJETIVO] for f in filas)),
    )

    if (
        profundidad >= max_profundidad
        or gini(filas) == 0
        or len(filas) < 2 * min_muestras_hoja
    ):
        return nodo

    mejor = mejor_division(filas, min_muestras_hoja)
    if mejor is None or mejor[0] <= 0:
        return nodo

    _, variable, valor, categorica, izquierda, derecha = mejor
    nodo.variable = variable
    nodo.valor = valor
    nodo.categorica = categorica
    nodo.izquierda = construir_arbol(
        izquierda, profundidad + 1, max_profundidad, min_muestras_hoja
    )
    nodo.derecha = construir_arbol(
        derecha, profundidad + 1, max_profundidad, min_muestras_hoja
    )
    return nodo


def predecir(arbol, fila):
    nodo = arbol
    while nodo.variable is not None:
        if nodo.categorica:
            cumple = fila[nodo.variable] == nodo.valor
        else:
            cumple = fila[nodo.variable] <= nodo.valor
        nodo = nodo.izquierda if cumple else nodo.derecha
    return nodo.prediccion


def division_estratificada(filas, proporcion_prueba=0.25, semilla=42):
    generador = random.Random(semilla)
    grupos = {clase: [] for clase in CLASES}

    for fila in filas:
        grupos[fila[OBJETIVO]].append(fila)

    entrenamiento, prueba = [], []
    for clase in CLASES:
        grupo = grupos[clase][:]
        generador.shuffle(grupo)
        cantidad_prueba = round(len(grupo) * proporcion_prueba)
        prueba.extend(grupo[:cantidad_prueba])
        entrenamiento.extend(grupo[cantidad_prueba:])

    generador.shuffle(entrenamiento)
    generador.shuffle(prueba)
    return entrenamiento, prueba


def matriz_confusion(reales, predicciones):
    matriz = {real: {pred: 0 for pred in CLASES} for real in CLASES}
    for real, pred in zip(reales, predicciones):
        matriz[real][pred] += 1
    return matriz


def metricas_por_clase(reales, predicciones):
    resultados = {}
    for clase in CLASES:
        vp = sum(r == clase and p == clase for r, p in zip(reales, predicciones))
        fp = sum(r != clase and p == clase for r, p in zip(reales, predicciones))
        fn = sum(r == clase and p != clase for r, p in zip(reales, predicciones))
        soporte = sum(r == clase for r in reales)

        precision = vp / (vp + fp) if (vp + fp) else 0.0
        recall = vp / (vp + fn) if (vp + fn) else 0.0
        f1 = (
            2 * precision * recall / (precision + recall)
            if (precision + recall)
            else 0.0
        )
        resultados[clase] = (precision, recall, f1, soporte)
    return resultados


def guardar_reporte(total, entrenamiento, prueba, exactitud, metricas, matriz):
    with (RESULTADOS / "reporte_clasificacion.txt").open("w", encoding="utf-8") as archivo:
        archivo.write(f"Registros totales: {total}\n")
        archivo.write(f"Entrenamiento: {entrenamiento}\n")
        archivo.write(f"Prueba: {prueba}\n")
        archivo.write(f"Accuracy: {exactitud:.4f}\n\n")
        archivo.write("Clase       Precision  Recall  F1      Soporte\n")
        for clase in CLASES:
            precision, recall, f1, soporte = metricas[clase]
            archivo.write(
                f"{clase:<11} {precision:>8.3f} {recall:>7.3f} "
                f"{f1:>7.3f} {soporte:>8}\n"
            )
        archivo.write("\nMatriz de confusion (filas=real, columnas=prediccion)\n")
        archivo.write("             Normal  Demorado  Critico\n")
        for clase in CLASES:
            archivo.write(
                f"{clase:<11} "
                + " ".join(f"{matriz[clase][pred]:>8}" for pred in CLASES)
                + "\n"
            )


def guardar_predicciones(prueba, predicciones):
    campos = FEATURES + ["real", "prediccion"]
    with (RESULTADOS / "predicciones_prueba.csv").open(
        "w", encoding="utf-8", newline=""
    ) as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=campos)
        escritor.writeheader()
        for fila, pred in zip(prueba, predicciones):
            salida = {campo: fila[campo] for campo in FEATURES}
            salida["real"] = fila[OBJETIVO]
            salida["prediccion"] = pred
            escritor.writerow(salida)


def guardar_matriz_svg(matriz):
    ancho, alto = 720, 560
    margen_x, margen_y = 210, 130
    celda = 100
    partes = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{ancho}" height="{alto}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<text x="360" y="45" text-anchor="middle" font-family="Arial" '
        'font-size="24" font-weight="bold">Matriz de confusion</text>',
        '<text x="360" y="78" text-anchor="middle" font-family="Arial" '
        'font-size="15">Columnas: prediccion / Filas: valor real</text>',
    ]

    for j, clase in enumerate(CLASES):
        x = margen_x + j * celda + celda / 2
        partes.append(
            f'<text x="{x}" y="{margen_y - 18}" text-anchor="middle" '
            f'font-family="Arial" font-size="14">{html.escape(clase)}</text>'
        )

    for i, real in enumerate(CLASES):
        y = margen_y + i * celda
        partes.append(
            f'<text x="{margen_x - 20}" y="{y + 58}" text-anchor="end" '
            f'font-family="Arial" font-size="14">{html.escape(real)}</text>'
        )
        for j, pred in enumerate(CLASES):
            x = margen_x + j * celda
            valor = matriz[real][pred]
            relleno = "#dbeafe" if i == j else "#f3f4f6"
            partes.append(
                f'<rect x="{x}" y="{y}" width="{celda}" height="{celda}" '
                f'fill="{relleno}" stroke="#475569"/>'
            )
            partes.append(
                f'<text x="{x + celda/2}" y="{y + 62}" text-anchor="middle" '
                f'font-family="Arial" font-size="30" font-weight="bold">{valor}</text>'
            )

    partes.append("</svg>")
    (RESULTADOS / "matriz_confusion.svg").write_text("\n".join(partes), encoding="utf-8")


def condicion_nodo(nodo):
    if nodo.variable is None:
        return f"Predice: {nodo.prediccion}"
    if nodo.categorica:
        return f"{nodo.variable} = {nodo.valor}"
    return f"{nodo.variable} <= {nodo.valor:.2f}"


def guardar_arbol_svg(arbol):
    # Se muestran los primeros cuatro niveles para que la figura siga siendo legible.
    max_nivel = 3
    nodos = []

    def recorrer(nodo, nivel, indice):
        if nodo is None or nivel > max_nivel:
            return
        nodos.append((nodo, nivel, indice))
        recorrer(nodo.izquierda, nivel + 1, indice * 2)
        recorrer(nodo.derecha, nivel + 1, indice * 2 + 1)

    recorrer(arbol, 0, 0)

    ancho, alto = 1500, 720
    margen = 70
    coords = {}
    for nodo, nivel, indice in nodos:
        columnas = 2 ** nivel
        x = margen + (indice + 0.5) * ((ancho - 2 * margen) / columnas)
        y = 80 + nivel * 170
        coords[id(nodo)] = (x, y)

    partes = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{ancho}" height="{alto}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<text x="750" y="38" text-anchor="middle" font-family="Arial" '
        'font-size="24" font-weight="bold">Arbol de decision entrenado</text>',
    ]

    for nodo, nivel, _ in nodos:
        x, y = coords[id(nodo)]
        if nivel < max_nivel:
            for hijo in (nodo.izquierda, nodo.derecha):
                if hijo is not None and id(hijo) in coords:
                    hx, hy = coords[id(hijo)]
                    partes.append(
                        f'<line x1="{x}" y1="{y+38}" x2="{hx}" y2="{hy-38}" '
                        'stroke="#64748b" stroke-width="2"/>'
                    )

    for nodo, _, _ in nodos:
        x, y = coords[id(nodo)]
        texto = html.escape(condicion_nodo(nodo))
        pred = html.escape(nodo.prediccion)
        partes.append(
            f'<rect x="{x-105}" y="{y-38}" width="210" height="76" rx="10" '
            'fill="#eef2ff" stroke="#334155"/>'
        )
        partes.append(
            f'<text x="{x}" y="{y-5}" text-anchor="middle" font-family="Arial" '
            f'font-size="13">{texto}</text>'
        )
        partes.append(
            f'<text x="{x}" y="{y+18}" text-anchor="middle" font-family="Arial" '
            f'font-size="12" font-weight="bold">Clase: {pred}</text>'
        )

    partes.append("</svg>")
    (RESULTADOS / "arbol_decision.svg").write_text("\n".join(partes), encoding="utf-8")


def entrenar_y_evaluar():
    filas = cargar_dataset()
    entrenamiento, prueba = division_estratificada(
        filas, proporcion_prueba=0.25, semilla=42
    )

    arbol = construir_arbol(
        entrenamiento,
        max_profundidad=5,
        min_muestras_hoja=4,
    )

    predicciones = [predecir(arbol, fila) for fila in prueba]
    reales = [fila[OBJETIVO] for fila in prueba]
    aciertos = sum(real == pred for real, pred in zip(reales, predicciones))
    exactitud = aciertos / len(prueba)

    matriz = matriz_confusion(reales, predicciones)
    metricas = metricas_por_clase(reales, predicciones)

    RESULTADOS.mkdir(parents=True, exist_ok=True)
    guardar_reporte(
        len(filas), len(entrenamiento), len(prueba), exactitud, metricas, matriz
    )
    guardar_predicciones(prueba, predicciones)
    guardar_matriz_svg(matriz)
    guardar_arbol_svg(arbol)

    print("MODELO SUPERVISADO - ACTIVIDAD 5")
    print(f"Registros: {len(filas)}")
    print(f"Entrenamiento: {len(entrenamiento)} | Prueba: {len(prueba)}")
    print(f"Accuracy: {exactitud:.2%}")
    print("\nReporte de clasificacion:")
    print("Clase       Precision  Recall     F1  Soporte")
    for clase in CLASES:
        precision, recall, f1, soporte = metricas[clase]
        print(
            f"{clase:<11} {precision:>8.3f} {recall:>7.3f} "
            f"{f1:>7.3f} {soporte:>8}"
        )

    print("\nMatriz de confusion:")
    print("             Normal  Demorado  Critico")
    for real in CLASES:
        print(
            f"{real:<11} "
            + " ".join(f"{matriz[real][pred]:>8}" for pred in CLASES)
        )

    print(f"\nResultados guardados en: {RESULTADOS}")
    print("Archivos visuales: matriz_confusion.svg y arbol_decision.svg")


if __name__ == "__main__":
    entrenar_y_evaluar()
