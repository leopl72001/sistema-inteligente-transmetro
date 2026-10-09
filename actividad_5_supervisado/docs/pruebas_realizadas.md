# Pruebas realizadas al componente supervisado

## Pruebas de integridad del dataset

Se incluyeron cinco pruebas automatizadas:

1. El dataset contiene 420 registros.
2. La variable objetivo no contiene valores nulos.
3. Existen exactamente las clases Normal, Demorado y Critico.
4. Origen y destino son diferentes en cada observación.
5. Las variables hora_pico, lluvia e incidente contienen únicamente 0 y 1.

Comando:

    python -m unittest actividad_5_supervisado.tests.test_modelo -v

Resultado esperado:

    Ran 5 tests
    OK

## Prueba del modelo

El dataset se divide de manera estratificada en 75 % para entrenamiento y 25 % para prueba usando una semilla fija de 42. Esto produce 315 registros de entrenamiento y 105 registros de prueba.

El clasificador es un árbol de decisión implementado en Python estándar con profundidad máxima 5 y mínimo de 4 muestras por hoja.

Resultados de referencia:

- Registros totales: 420.
- Entrenamiento: 315.
- Prueba: 105.
- Accuracy: 93.33 %.

Matriz de confusión de referencia, en el orden Normal / Demorado / Critico:

    [[69, 1, 0],
     [ 3,22, 0],
     [ 1, 2, 7]]

Interpretación:

- De 70 casos Normal, 69 se clasifican correctamente.
- De 25 casos Demorado, 22 se clasifican correctamente.
- De 10 casos Critico, 7 se clasifican correctamente.
- El resultado global sigue siendo 93.33 %.

## Evidencias generadas

La ejecución del modelo crea automáticamente:

- matriz_confusion.svg
- arbol_decision.svg
- reporte_clasificacion.txt
- predicciones_prueba.csv

Estas evidencias pueden utilizarse en el documento final y en el video de presentación.
