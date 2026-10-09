"""Actividad 4 - Aprendizaje no supervisado con K-Means.

Implementacion con Python estandar para evitar dependencias externas.
Agrupa recorridos de Transmetro de acuerdo con similitud operacional.
"""

from __future__ import annotations

import csv
import math
import random
import statistics
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
DATASET = BASE / "data" / "datos_transmetro_no_supervisado.csv"
RESULTADOS = BASE / "resultados"

VARIABLES = [
    "numero_paradas",
    "hora",
    "hora_pico",
    "pasajeros",
    "lluvia",
    "tiempo_base_min",
]

K = 3
SEMILLA = 42
MAX_ITERACIONES = 100


def cargar_datos():
    with DATASET.open("r", encoding="utf-8", newline="") as archivo:
        filas = list(csv.DictReader(archivo))

    for fila in filas:
        fila["id"] = int(fila["id"])
        for variable in VARIABLES:
            fila[variable] = float(fila[variable])
        fila["incidente"] = int(fila["incidente"])
    return filas


def estandarizar(filas):
    medias = {}
    desviaciones = {}

    for variable in VARIABLES:
        valores = [fila[variable] for fila in filas]
        medias[variable] = statistics.mean(valores)
        desviaciones[variable] = statistics.pstdev(valores) or 1.0

    datos = []
    for fila in filas:
        datos.append([
            (fila[variable] - medias[variable]) / desviaciones[variable]
            for variable in VARIABLES
        ])
    return datos, medias, desviaciones


def distancia_cuadrada(a, b):
    return sum((x - y) ** 2 for x, y in zip(a, b))


def inicializar_centroides(datos, k, semilla=42):
    rng = random.Random(semilla)
    centroides = [datos[rng.randrange(len(datos))][:]]

    while len(centroides) < k:
        distancias = [
            min(distancia_cuadrada(punto, centro) for centro in centroides)
            for punto in datos
        ]
        total = sum(distancias)

        if total == 0:
            centroides.append(datos[rng.randrange(len(datos))][:])
            continue

        objetivo = rng.random() * total
        acumulado = 0.0
        seleccionado = 0
        for i, valor in enumerate(distancias):
            acumulado += valor
            if acumulado >= objetivo:
                seleccionado = i
                break
        centroides.append(datos[seleccionado][:])

    return centroides


def entrenar_kmeans(datos, k=K, semilla=SEMILLA, max_iteraciones=MAX_ITERACIONES):
    centroides = inicializar_centroides(datos, k, semilla)
    etiquetas = None

    for iteracion in range(1, max_iteraciones + 1):
        nuevas_etiquetas = [
            min(
                range(k),
                key=lambda grupo: distancia_cuadrada(punto, centroides[grupo]),
            )
            for punto in datos
        ]

        nuevos_centroides = []
        for grupo in range(k):
            puntos = [
                punto
                for punto, etiqueta in zip(datos, nuevas_etiquetas)
                if etiqueta == grupo
            ]

            if not puntos:
                nuevos_centroides.append(centroides[grupo][:])
            else:
                nuevos_centroides.append([
                    sum(columna) / len(puntos)
                    for columna in zip(*puntos)
                ])

        if nuevas_etiquetas == etiquetas:
            centroides = nuevos_centroides
            etiquetas = nuevas_etiquetas
            break

        centroides = nuevos_centroides
        etiquetas = nuevas_etiquetas

    inercia = sum(
        distancia_cuadrada(punto, centroides[etiqueta])
        for punto, etiqueta in zip(datos, etiquetas)
    )

    return etiquetas, centroides, inercia, iteracion


def calcular_silhouette(datos, etiquetas, k=K):
    grupos = {
        grupo: [i for i, etiqueta in enumerate(etiquetas) if etiqueta == grupo]
        for grupo in range(k)
    }

    valores = []
    for i, punto in enumerate(datos):
        grupo_propio = etiquetas[i]
        propios = grupos[grupo_propio]

        if len(propios) <= 1:
            valores.append(0.0)
            continue

        a = sum(
            math.sqrt(distancia_cuadrada(punto, datos[j]))
            for j in propios
            if j != i
        ) / (len(propios) - 1)

        b = min(
            sum(
                math.sqrt(distancia_cuadrada(punto, datos[j]))
                for j in indices
            ) / len(indices)
            for grupo, indices in grupos.items()
            if grupo != grupo_propio and indices
        )

        valores.append((b - a) / max(a, b) if max(a, b) else 0.0)

    return sum(valores) / len(valores)


def desestandarizar_centroides(centroides, medias, desviaciones):
    resultado = []
    for centro in centroides:
        resultado.append({
            variable: medias[variable] + valor * desviaciones[variable]
            for variable, valor in zip(VARIABLES, centro)
        })
    return resultado


def guardar_clusters(filas, etiquetas):
    RESULTADOS.mkdir(parents=True, exist_ok=True)
    campos = [
        "id", "origen", "destino", "numero_paradas", "hora", "hora_pico",
        "tipo_dia", "pasajeros", "lluvia", "incidente", "tiempo_base_min",
        "cluster",
    ]

    with (RESULTADOS / "clusters.csv").open(
        "w", encoding="utf-8", newline=""
    ) as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=campos)
        escritor.writeheader()

        for fila, etiqueta in zip(filas, etiquetas):
            salida = {campo: fila[campo] for campo in campos if campo != "cluster"}
            salida["cluster"] = etiqueta + 1
            escritor.writerow(salida)


def guardar_resumen(centroides, etiquetas, inercia, silhouette, iteraciones):
    conteos = [etiquetas.count(i) for i in range(K)]

    with (RESULTADOS / "resumen_clusters.txt").open(
        "w", encoding="utf-8"
    ) as archivo:
        archivo.write("APRENDIZAJE NO SUPERVISADO - K-MEANS\n")
        archivo.write(f"Registros: {len(etiquetas)}\n")
        archivo.write(f"Numero de clusters: {K}\n")
        archivo.write(f"Iteraciones: {iteraciones}\n")
        archivo.write(f"Inercia: {inercia:.4f}\n")
        archivo.write(f"Silhouette promedio: {silhouette:.4f}\n\n")

        for i, centro in enumerate(centroides):
            archivo.write(f"CLUSTER {i + 1} - {conteos[i]} registros\n")
            for variable in VARIABLES:
                archivo.write(f"  {variable}: {centro[variable]:.2f}\n")
            archivo.write("\n")


def guardar_visualizacion_svg(filas, etiquetas):
    ancho, alto = 900, 560
    margen_izq, margen_inf, margen_sup, margen_der = 80, 70, 60, 40

    xs = [fila["tiempo_base_min"] for fila in filas]
    ys = [fila["pasajeros"] for fila in filas]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    colores = ["#2563eb", "#ea580c", "#16a34a"]

    def sx(x):
        return margen_izq + (x - min_x) / (max_x - min_x) * (
            ancho - margen_izq - margen_der
        )

    def sy(y):
        return alto - margen_inf - (y - min_y) / (max_y - min_y) * (
            alto - margen_inf - margen_sup
        )

    partes = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{ancho}" height="{alto}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<text x="450" y="34" text-anchor="middle" font-family="Arial" '
        'font-size="24" font-weight="bold">Clusters operativos de Transmetro</text>',
        f'<line x1="{margen_izq}" y1="{alto-margen_inf}" '
        f'x2="{ancho-margen_der}" y2="{alto-margen_inf}" stroke="#111827"/>',
        f'<line x1="{margen_izq}" y1="{margen_sup}" '
        f'x2="{margen_izq}" y2="{alto-margen_inf}" stroke="#111827"/>',
    ]

    for fila, etiqueta in zip(filas, etiquetas):
        partes.append(
            f'<circle cx="{sx(fila["tiempo_base_min"]):.1f}" '
            f'cy="{sy(fila["pasajeros"]):.1f}" r="4" '
            f'fill="{colores[etiqueta]}" fill-opacity="0.58"/>'
        )

    partes.append(
        f'<text x="{ancho/2}" y="{alto-20}" text-anchor="middle" '
        'font-family="Arial" font-size="15">Tiempo base del recorrido (minutos)</text>'
    )
    partes.append(
        f'<text x="22" y="{alto/2}" text-anchor="middle" '
        'font-family="Arial" font-size="15" '
        f'transform="rotate(-90 22 {alto/2})">Pasajeros estimados</text>'
    )

    for i, color in enumerate(colores):
        x = 610 + i * 95
        partes.append(f'<circle cx="{x}" cy="52" r="6" fill="{color}"/>')
        partes.append(
            f'<text x="{x+10}" y="57" font-family="Arial" font-size="13">'
            f'Cluster {i+1}</text>'
        )

    partes.append("</svg>")
    (RESULTADOS / "clusters.svg").write_text("\n".join(partes), encoding="utf-8")


def interpretar_clusters(centroides, etiquetas):
    conteos = [etiquetas.count(i) for i in range(K)]
    orden_pasajeros = sorted(range(K), key=lambda i: centroides[i]["pasajeros"])
    mas_bajo, medio, mas_alto = orden_pasajeros

    nombres = {
        mas_bajo: "Baja demanda y recorridos cortos",
        medio: "Recorridos largos de demanda media",
        mas_alto: "Alta demanda asociada a horas pico",
    }

    with (RESULTADOS / "interpretacion_clusters.txt").open(
        "w", encoding="utf-8"
    ) as archivo:
        for i in range(K):
            archivo.write(
                f"Cluster {i+1}: {nombres[i]} ({conteos[i]} registros)\n"
            )


def main():
    filas = cargar_datos()
    datos, medias, desviaciones = estandarizar(filas)

    etiquetas, centroides_z, inercia, iteraciones = entrenar_kmeans(datos)
    silhouette = calcular_silhouette(datos, etiquetas)
    centroides = desestandarizar_centroides(
        centroides_z, medias, desviaciones
    )

    guardar_clusters(filas, etiquetas)
    guardar_resumen(
        centroides, etiquetas, inercia, silhouette, iteraciones
    )
    guardar_visualizacion_svg(filas, etiquetas)
    interpretar_clusters(centroides, etiquetas)

    conteos = [etiquetas.count(i) for i in range(K)]

    print("APRENDIZAJE NO SUPERVISADO - K-MEANS")
    print(f"Registros: {len(filas)}")
    print(f"Clusters: {K}")
    print(f"Iteraciones: {iteraciones}")
    print(f"Inercia: {inercia:.2f}")
    print(f"Silhouette promedio: {silhouette:.3f}")
    print()

    for i, centro in enumerate(centroides):
        print(f"CLUSTER {i + 1}: {conteos[i]} registros")
        print(f"  Numero de paradas promedio: {centro['numero_paradas']:.2f}")
        print(f"  Hora promedio: {centro['hora']:.2f}")
        print(f"  Proporcion hora pico: {centro['hora_pico']:.2f}")
        print(f"  Pasajeros promedio: {centro['pasajeros']:.2f}")
        print(f"  Proporcion lluvia: {centro['lluvia']:.2f}")
        print(f"  Tiempo base promedio: {centro['tiempo_base_min']:.2f} min")
        print()

    print(f"Resultados guardados en: {RESULTADOS}")


if __name__ == "__main__":
    main()
