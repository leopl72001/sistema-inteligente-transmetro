import unittest

from src.base_conocimiento import ESTACIONES, construir_grafo
from src.busqueda import a_estrella, costo_uniforme, heuristica


class TestSistemaInteligente(unittest.TestCase):
    def setUp(self):
        self.grafo = construir_grafo()

    def test_base_conocimiento_contiene_estaciones(self):
        self.assertEqual(len(ESTACIONES), 11)
        self.assertIn("Portal de Soledad", self.grafo)
        self.assertIn("La Arenosa", self.grafo)

    def test_reglas_son_bidireccionales(self):
        vecinos_portal = [v[0] for v in self.grafo["Portal de Soledad"]]
        vecinos_pacho = [v[0] for v in self.grafo["Pacho Galan"]]
        self.assertIn("Pacho Galan", vecinos_portal)
        self.assertIn("Portal de Soledad", vecinos_pacho)

    def test_a_estrella_encuentra_ruta_optima(self):
        ruta, costo, _ = a_estrella(self.grafo, "Portal de Soledad", "La Arenosa")
        self.assertEqual(costo, 23)
        self.assertEqual(ruta[0], "Portal de Soledad")
        self.assertEqual(ruta[-1], "La Arenosa")

    def test_a_estrella_y_costo_uniforme_coinciden(self):
        _, costo_a, _ = a_estrella(self.grafo, "Pacho Galan", "Atlantico")
        _, costo_u, _ = costo_uniforme(self.grafo, "Pacho Galan", "Atlantico")
        self.assertEqual(costo_a, costo_u)

    def test_heuristica_destino_es_cero(self):
        self.assertEqual(heuristica("La Arenosa", "La Arenosa"), 0)

    def test_estacion_invalida(self):
        with self.assertRaises(ValueError):
            a_estrella(self.grafo, "Estacion Inventada", "La Arenosa")


if __name__ == "__main__":
    unittest.main()
