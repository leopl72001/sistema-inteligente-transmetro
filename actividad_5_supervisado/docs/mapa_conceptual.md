# Mapa conceptual - Aprendizaje supervisado aplicado a Transmetro

```mermaid
flowchart TD
    A[Fuente de datos] --> B[Dataset sintetico]
    B --> C[Variables de entrada]
    C --> C1[Origen y destino]
    C --> C2[Hora y hora pico]
    C --> C3[Pasajeros]
    C --> C4[Lluvia e incidente]
    C --> C5[Tiempo base]
    B --> D[Variable objetivo]
    D --> D1[Normal]
    D --> D2[Demorado]
    D --> D3[Critico]
    C --> E[Preprocesamiento]
    E --> F[Division entrenamiento y prueba]
    F --> G[Arbol de decision]
    G --> H[Predicciones]
    H --> I[Evaluacion]
    I --> I1[Accuracy]
    I --> I2[Matriz de confusion]
    I --> I3[Precision Recall F1]
```

## Idea central

El aprendizaje supervisado utiliza ejemplos que ya tienen una etiqueta conocida. En este proyecto, cada registro contiene condiciones del recorrido y un estado del servicio. El árbol de decisión aprende patrones de los datos de entrenamiento y posteriormente clasifica registros que no utilizó durante el aprendizaje.
