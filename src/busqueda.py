"""Algoritmos de busqueda para encontrar rutas en la base de conocimiento."""

import heapq
from typing import Dict, List, Tuple

from .base_conocimiento import POSICION


Resultado = Tuple[List[str], int, int]


def _validar_estaciones(grafo: Dict, origen: str, destino: str) -> None:
    if origen not in grafo:
        raise ValueError(f"Estacion de origen no valida: {origen}")
    if destino not in grafo:
        raise ValueError(f"Estacion de destino no valida: {destino}")


def reconstruir_ruta(padres: Dict[str, str | None], destino: str) -> List[str]:
    ruta = []
    actual = destino
    while actual is not None:
        ruta.append(actual)
        actual = padres[actual]
    return list(reversed(ruta))


def costo_uniforme(grafo: Dict[str, List[tuple]], origen: str, destino: str) -> Resultado:
    """Busqueda de costo uniforme (equivalente a Dijkstra con costos positivos)."""
    _validar_estaciones(grafo, origen, destino)

    frontera = [(0, origen)]
    costos = {origen: 0}
    padres = {origen: None}
    expandidos = 0

    while frontera:
        costo_actual, actual = heapq.heappop(frontera)
        if costo_actual != costos[actual]:
            continue

        expandidos += 1
        if actual == destino:
            return reconstruir_ruta(padres, destino), costo_actual, expandidos

        for vecino, costo_arista, _tipo in grafo[actual]:
            nuevo_costo = costo_actual + costo_arista
            if nuevo_costo < costos.get(vecino, float("inf")):
                costos[vecino] = nuevo_costo
                padres[vecino] = actual
                heapq.heappush(frontera, (nuevo_costo, vecino))

    raise ValueError("No existe una ruta entre las estaciones indicadas")


def heuristica(estacion: str, destino: str) -> float:
    """Estimacion optimista del costo restante.

    Se usa la distancia relativa entre estaciones multiplicada por 1.5 minutos.
    En el modelo, ninguna conexion cuesta menos de este limite por posicion
    recorrida, por lo que la heuristica no sobreestima el costo real.
    """
    return abs(POSICION[estacion] - POSICION[destino]) * 1.5


def a_estrella(grafo: Dict[str, List[tuple]], origen: str, destino: str) -> Resultado:
    """Busqueda A* usando g(n) + h(n)."""
    _validar_estaciones(grafo, origen, destino)

    frontera = [(heuristica(origen, destino), 0, origen)]
    costos = {origen: 0}
    padres = {origen: None}
    expandidos = 0

    while frontera:
        _f, costo_actual, actual = heapq.heappop(frontera)
        if costo_actual != costos[actual]:
            continue

        expandidos += 1
        if actual == destino:
            return reconstruir_ruta(padres, destino), costo_actual, expandidos

        for vecino, costo_arista, _tipo in grafo[actual]:
            nuevo_costo = costo_actual + costo_arista
            if nuevo_costo < costos.get(vecino, float("inf")):
                costos[vecino] = nuevo_costo
                padres[vecino] = actual
                prioridad = nuevo_costo + heuristica(vecino, destino)
                heapq.heappush(frontera, (prioridad, nuevo_costo, vecino))

    raise ValueError("No existe una ruta entre las estaciones indicadas")


def detalle_tramos(grafo: Dict[str, List[tuple]], ruta: List[str]) -> List[tuple]:
    """Retorna origen, destino, costo y tipo para cada tramo de la ruta."""
    tramos = []
    for origen, destino in zip(ruta, ruta[1:]):
        for vecino, costo, tipo in grafo[origen]:
            if vecino == destino:
                tramos.append((origen, destino, costo, tipo))
                break
    return tramos
