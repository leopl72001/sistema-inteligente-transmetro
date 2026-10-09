import csv
import unittest
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
DATASET = BASE / "data" / "datos_transmetro_supervisado.csv"


def cargar_filas():
    with DATASET.open("r", encoding="utf-8", newline="") as archivo:
        return list(csv.DictReader(archivo))


class TestActividad5(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.filas = cargar_filas()

    def test_dataset_tiene_420_registros(self):
        self.assertEqual(len(self.filas), 420)

    def test_variable_objetivo_sin_nulos(self):
        self.assertTrue(all(fila["estado_servicio"] for fila in self.filas))

    def test_clases_esperadas(self):
        clases = {fila["estado_servicio"] for fila in self.filas}
        self.assertEqual(clases, {"Normal", "Demorado", "Critico"})

    def test_origen_y_destino_son_distintos(self):
        self.assertTrue(
            all(fila["origen"] != fila["destino"] for fila in self.filas)
        )

    def test_variables_binarias_validas(self):
        for columna in ["hora_pico", "lluvia", "incidente"]:
            valores = {fila[columna] for fila in self.filas}
            self.assertTrue(valores.issubset({"0", "1"}))


if __name__ == "__main__":
    unittest.main()
