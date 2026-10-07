import unittest
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parents[1]
DATASET = BASE / "data" / "datos_transmetro_supervisado.csv"


class TestActividad5(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.df = pd.read_csv(DATASET)

    def test_dataset_tiene_420_registros(self):
        self.assertEqual(len(self.df), 420)

    def test_variable_objetivo_sin_nulos(self):
        self.assertFalse(self.df["estado_servicio"].isna().any())

    def test_clases_esperadas(self):
        self.assertEqual(
            set(self.df["estado_servicio"].unique()),
            {"Normal", "Demorado", "Critico"},
        )

    def test_origen_y_destino_son_distintos(self):
        self.assertTrue((self.df["origen"] != self.df["destino"]).all())

    def test_variables_binarias_validas(self):
        for columna in ["hora_pico", "lluvia", "incidente"]:
            self.assertTrue(set(self.df[columna].unique()).issubset({0, 1}))


if __name__ == "__main__":
    unittest.main()
