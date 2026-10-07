"""Genera de forma reproducible el dataset sintetico de la Actividad 5."""

from pathlib import Path

ESTACIONES = [
    "Portal de Soledad", "Pacho Galan", "Pedro Ramaya Beltran",
    "Joaquin Barrios Polo", "Buenos Aires", "La Ocho", "La Catorce",
    "La Veintiuna", "Atlantico", "Chiquinquira", "La Arenosa",
]
CLASES = ["Normal", "Demorado", "Critico"]


class LCG:
    def __init__(self, seed=42):
        self.state = seed & 0xFFFFFFFF

    def random(self):
        self.state = (1664525 * self.state + 1013904223) & 0xFFFFFFFF
        return self.state / 2**32

    def randint(self, a, b):
        return a + int(self.random() * (b - a + 1))

    def normal(self, mu, sigma):
        z = sum(self.random() for _ in range(12)) - 6
        return mu + sigma * z


def generar_filas(cantidad=420):
    rng = LCG(42)
    filas = []
    for i in range(1, cantidad + 1):
        origen_idx = int(rng.random() * len(ESTACIONES))
        destino_idx = int(rng.random() * (len(ESTACIONES) - 1))
        if destino_idx >= origen_idx:
            destino_idx += 1

        numero_paradas = abs(destino_idx - origen_idx)
        r = rng.random()
        tipo_dia = "Habil" if r < 0.68 else ("Sabado" if r < 0.86 else "Domingo")
        hora = rng.randint(5, 22)
        hora_pico = int((6 <= hora <= 8) or (16 <= hora <= 19))

        base_pasajeros = 45 + 38 * hora_pico + (8 if tipo_dia == "Habil" else -7)
        pasajeros = int(max(10, min(145, round(rng.normal(base_pasajeros, 18)))))
        lluvia = int(rng.random() < 0.24)
        incidente = int(rng.random() < 0.14)
        tiempo_base = round(4 + 2.6 * numero_paradas, 1)

        if incidente and (hora_pico or pasajeros >= 70 or lluvia):
            estado = "Critico"
        elif incidente:
            estado = "Demorado"
        elif (hora_pico and lluvia) or pasajeros >= 95 or (lluvia and pasajeros >= 70):
            estado = "Demorado"
        else:
            estado = "Normal"

        demora_base = {"Normal": 3.5, "Demorado": 11.5, "Critico": 23}[estado]
        demora = round(max(0, rng.normal(demora_base, 2.0)), 1)

        # 5 % de ruido para evitar un conjunto artificialmente perfecto.
        if rng.random() < 0.05:
            opciones = [c for c in CLASES if c != estado]
            estado = opciones[int(rng.random() * len(opciones))]

        filas.append([
            i, ESTACIONES[origen_idx], ESTACIONES[destino_idx], numero_paradas,
            hora, hora_pico, tipo_dia, pasajeros, lluvia, incidente,
            tiempo_base, demora, estado,
        ])
    return filas


def main():
    destino = Path(__file__).resolve().parents[1] / "data" / "datos_transmetro_supervisado.csv"
    destino.parent.mkdir(parents=True, exist_ok=True)
    encabezado = [
        "id", "origen", "destino", "numero_paradas", "hora", "hora_pico",
        "tipo_dia", "pasajeros", "lluvia", "incidente", "tiempo_base_min",
        "demora_min", "estado_servicio",
    ]
    with destino.open("w", encoding="utf-8", newline="") as archivo:
        archivo.write(",".join(encabezado) + "\n")
        for fila in generar_filas():
            archivo.write(",".join(map(str, fila)) + "\n")
    print(f"Dataset generado: {destino}")


if __name__ == "__main__":
    main()
