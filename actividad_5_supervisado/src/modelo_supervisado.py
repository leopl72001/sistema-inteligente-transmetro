"""Modelo supervisado con arbol de decision para clasificar el estado del servicio."""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.metrics import ConfusionMatrixDisplay, accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.tree import DecisionTreeClassifier, plot_tree


BASE = Path(__file__).resolve().parents[1]
DATASET = BASE / "data" / "datos_transmetro_supervisado.csv"
RESULTADOS = BASE / "resultados"

FEATURES = [
    "origen", "destino", "numero_paradas", "hora", "hora_pico",
    "tipo_dia", "pasajeros", "lluvia", "incidente", "tiempo_base_min",
]
OBJETIVO = "estado_servicio"
CATEGORICAS = ["origen", "destino", "tipo_dia"]
NUMERICAS = [c for c in FEATURES if c not in CATEGORICAS]


def construir_modelo():
    preprocesamiento = ColumnTransformer(
        [
            ("categoricas", OneHotEncoder(handle_unknown="ignore"), CATEGORICAS),
            ("numericas", "passthrough", NUMERICAS),
        ]
    )
    arbol = DecisionTreeClassifier(
        max_depth=5,
        min_samples_leaf=4,
        random_state=42,
    )
    return Pipeline([
        ("preprocesamiento", preprocesamiento),
        ("modelo", arbol),
    ])


def entrenar_y_evaluar():
    df = pd.read_csv(DATASET)
    X = df[FEATURES]
    y = df[OBJETIVO]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.25,
        random_state=42,
        stratify=y,
    )

    modelo = construir_modelo()
    modelo.fit(X_train, y_train)
    pred = modelo.predict(X_test)

    exactitud = accuracy_score(y_test, pred)
    reporte = classification_report(y_test, pred, digits=3)

    RESULTADOS.mkdir(parents=True, exist_ok=True)

    with (RESULTADOS / "reporte_clasificacion.txt").open("w", encoding="utf-8") as f:
        f.write(f"Registros totales: {len(df)}\n")
        f.write(f"Entrenamiento: {len(X_train)}\n")
        f.write(f"Prueba: {len(X_test)}\n")
        f.write(f"Accuracy: {exactitud:.4f}\n\n")
        f.write(reporte)

    salida = X_test.copy()
    salida["real"] = y_test.values
    salida["prediccion"] = pred
    salida.to_csv(RESULTADOS / "predicciones_prueba.csv", index=False)

    disp = ConfusionMatrixDisplay.from_predictions(
        y_test,
        pred,
        labels=["Normal", "Demorado", "Critico"],
        cmap="Blues",
        colorbar=False,
    )
    disp.ax_.set_title("Matriz de confusion - Arbol de decision")
    plt.tight_layout()
    plt.savefig(RESULTADOS / "matriz_confusion.png", dpi=180)
    plt.close()

    pre = modelo.named_steps["preprocesamiento"]
    arbol = modelo.named_steps["modelo"]
    nombres = pre.get_feature_names_out()

    plt.figure(figsize=(22, 11))
    plot_tree(
        arbol,
        feature_names=nombres,
        class_names=arbol.classes_,
        filled=True,
        rounded=True,
        max_depth=4,
        fontsize=7,
    )
    plt.title("Arbol de decision entrenado")
    plt.tight_layout()
    plt.savefig(RESULTADOS / "arbol_decision.png", dpi=180)
    plt.close()

    print("MODELO SUPERVISADO - ACTIVIDAD 5")
    print(f"Registros: {len(df)}")
    print(f"Entrenamiento: {len(X_train)} | Prueba: {len(X_test)}")
    print(f"Accuracy: {exactitud:.2%}")
    print("\nReporte de clasificacion:")
    print(reporte)
    print(f"Resultados guardados en: {RESULTADOS}")


if __name__ == "__main__":
    entrenar_y_evaluar()
