import csv
import importlib.util
import unittest
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
DATASET = BASE / "data" / "datos_transmetro_no_supervisado.csv"
MODELO_PATH = BASE / "src" / "modelo_no_supervisado.py"

spec = importlib.util.spec_from_file_location("modelo_no_supervisado", MODELO_PATH)
modelo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(modelo)


def cargar_filas():
    with DATASET.open("r", encoding="utf-8", newline="") as archivo:
        return list(csv.DictReader(archivo))


class TestActividadNoSupervisada(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.filas = cargar_filas()
        filas_modelo = modelo.cargar_datos()
        datos, _, _ = modelo.estandarizar(filas_modelo)
        cls.etiquetas, cls.centroides, _, _ = modelo.entrenar_kmeans(datos)

    def test_dataset_tiene_420_registros(self):
        self.assertEqual(len(self.filas), 420)

    def test_no_existe_variable_objetivo(self):
        columnas = set(self.filas[0].keys())
        self.assertNotIn("estado_servicio", columnas)
        self.assertNotIn("demora_min", columnas)

    def test_variables_requeridas_existen(self):
        columnas = set(self.filas[0].keys())
        for variable in modelo.VARIABLES:
            self.assertIn(variable, columnas)

    def test_kmeans_genera_tres_clusters(self):
        self.assertEqual(set(self.etiquetas), {0, 1, 2})

    def test_todos_los_registros_reciben_cluster(self):
        self.assertEqual(len(self.etiquetas), 420)

    def test_centroides_tienen_dimension_correcta(self):
        self.assertEqual(len(self.centroides), 3)
        self.assertTrue(
            all(len(centro) == len(modelo.VARIABLES) for centro in self.centroides)
        )


if __name__ == "__main__":
    unittest.main()
