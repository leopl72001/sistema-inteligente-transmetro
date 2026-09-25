"""Interfaz de consola del sistema inteligente de rutas."""

from src.base_conocimiento import ESTACIONES, construir_grafo
from src.busqueda import a_estrella, costo_uniforme, detalle_tramos


def mostrar_estaciones() -> None:
    print("\nESTACIONES DISPONIBLES")
    for i, estacion in enumerate(ESTACIONES, start=1):
        print(f"{i:>2}. {estacion}")


def seleccionar_estacion(mensaje: str) -> str:
    while True:
        try:
            numero = int(input(mensaje))
            if 1 <= numero <= len(ESTACIONES):
                return ESTACIONES[numero - 1]
        except ValueError:
            pass
        print("Opcion invalida. Ingrese el numero de una estacion.")


def imprimir_resultado(nombre: str, grafo, resultado) -> None:
    ruta, costo, expandidos = resultado
    print(f"\n--- {nombre} ---")
    print("Ruta:", " -> ".join(ruta))
    print(f"Costo total estimado: {costo} minutos")
    print(f"Nodos expandidos: {expandidos}")
    print("Tramos:")
    for origen, destino, costo_tramo, tipo in detalle_tramos(grafo, ruta):
        etiqueta = "corriente" if tipo == "corriente" else "expreso simulado"
        print(f"  {origen} -> {destino}: {costo_tramo} min ({etiqueta})")


def main() -> None:
    grafo = construir_grafo()
    print("SISTEMA INTELIGENTE DE RUTAS - TRANSMETRO")
    print("Modelo academico de la Troncal Murillo")
    print("Los tiempos usados son estimaciones para fines de demostracion.\n")

    mostrar_estaciones()
    origen = seleccionar_estacion("\nSeleccione el numero de la estacion de origen: ")
    destino = seleccionar_estacion("Seleccione el numero de la estacion de destino: ")

    if origen == destino:
        print("\nEl origen y el destino son la misma estacion. Costo: 0 minutos.")
        return

    resultado_ucs = costo_uniforme(grafo, origen, destino)
    resultado_astar = a_estrella(grafo, origen, destino)

    imprimir_resultado("Busqueda de costo uniforme", grafo, resultado_ucs)
    imprimir_resultado("Busqueda A*", grafo, resultado_astar)

    print("\nCOMPARACION")
    print(f"Costo uniforme expandio {resultado_ucs[2]} nodos.")
    print(f"A* expandio {resultado_astar[2]} nodos.")
    if resultado_astar[2] < resultado_ucs[2]:
        print("A* fue mas eficiente para esta consulta al usar informacion heuristica.")
    elif resultado_astar[2] == resultado_ucs[2]:
        print("Ambos algoritmos expandieron la misma cantidad de nodos en esta consulta.")
    else:
        print("En esta consulta particular, A* no redujo la cantidad de nodos expandidos.")


if __name__ == "__main__":
    main()
