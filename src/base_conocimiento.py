"""Base de conocimiento del sistema inteligente de rutas.

Las estaciones corresponden a la Troncal Murillo de Transmetro (Barranquilla/Soledad).
Los costos de viaje son valores academicos estimados en minutos para demostrar
la representacion por reglas y los algoritmos de busqueda; no son tiempos oficiales.
"""

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class ReglaConexion:
    origen: str
    destino: str
    costo: int
    tipo: str = "corriente"


ESTACIONES: List[str] = [
    "Portal de Soledad",
    "Pacho Galan",
    "Pedro Ramaya Beltran",
    "Joaquin Barrios Polo",
    "Buenos Aires",
    "La Ocho",
    "La Catorce",
    "La Veintiuna",
    "Atlantico",
    "Chiquinquira",
    "La Arenosa",
]

# Posicion relativa de cada estacion sobre el corredor. Se usa para la heuristica.
POSICION: Dict[str, int] = {estacion: i for i, estacion in enumerate(ESTACIONES)}

# Reglas logicas de conexion. La lectura conceptual de cada regla es:
# SI el usuario esta en ORIGEN Y existe conexion a DESTINO,
# ENTONCES puede desplazarse a DESTINO con el COSTO indicado.
REGLAS: List[ReglaConexion] = [
    ReglaConexion("Portal de Soledad", "Pacho Galan", 3),
    ReglaConexion("Pacho Galan", "Pedro Ramaya Beltran", 3),
    ReglaConexion("Pedro Ramaya Beltran", "Joaquin Barrios Polo", 4),
    ReglaConexion("Joaquin Barrios Polo", "Buenos Aires", 3),
    ReglaConexion("Buenos Aires", "La Ocho", 2),
    ReglaConexion("La Ocho", "La Catorce", 3),
    ReglaConexion("La Catorce", "La Veintiuna", 3),
    ReglaConexion("La Veintiuna", "Atlantico", 2),
    ReglaConexion("Atlantico", "Chiquinquira", 3),
    ReglaConexion("Chiquinquira", "La Arenosa", 3),
    # Conexiones expresas simuladas con fines academicos.
    ReglaConexion("Portal de Soledad", "Buenos Aires", 10, "expreso_simulado"),
    ReglaConexion("Buenos Aires", "La Catorce", 4, "expreso_simulado"),
    ReglaConexion("La Catorce", "Atlantico", 4, "expreso_simulado"),
    ReglaConexion("Atlantico", "La Arenosa", 5, "expreso_simulado"),
]


def construir_grafo() -> Dict[str, List[tuple]]:
    """Convierte las reglas en un grafo bidireccional.

    Cada regla se interpreta en ambos sentidos porque el modelo academico supone
    que el corredor puede recorrerse en ambas direcciones.
    """
    grafo: Dict[str, List[tuple]] = {estacion: [] for estacion in ESTACIONES}
    for regla in REGLAS:
        grafo[regla.origen].append((regla.destino, regla.costo, regla.tipo))
        grafo[regla.destino].append((regla.origen, regla.costo, regla.tipo))
    return grafo
