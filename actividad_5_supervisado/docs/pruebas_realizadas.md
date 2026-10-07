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

Resultado verificado:

    Ran 5 tests
    OK

## Prueba del modelo

El dataset se dividió de manera estratificada en 75 % para entrenamiento y 25 % para prueba, con random_state=42. La ejecución verificada produjo 315 registros de entrenamiento y 105 registros de prueba.

El clasificador utilizado es DecisionTreeClassifier con profundidad máxima 5 y mínimo de 4 muestras por hoja.

Resultados obtenidos y verificados:

- Registros totales: 420.
- Entrenamiento: 315.
- Prueba: 105.
- Accuracy: 93.33 %.
- Distribución total de clases: Normal 280, Demorado 101 y Critico 39.

Matriz de confusión, en el orden Normal / Demorado / Critico:

    [[70, 0, 0],
     [ 4,21, 0],
     [ 3, 0, 7]]

Interpretación:

- Los 70 casos Normal del conjunto de prueba fueron clasificados correctamente.
- De 25 casos Demorado, 21 fueron clasificados correctamente y 4 como Normal.
- De 10 casos Critico, 7 fueron clasificados correctamente y 3 como Normal.
- El modelo obtuvo precisión 1.000 para Critico y Demorado, aunque con recall de 0.700 y 0.840 respectivamente.
- El resultado no es perfecto, lo cual es coherente con el pequeño porcentaje de variación introducido en las etiquetas del dataset sintético.

## Evidencias generadas

La ejecución del modelo genera automáticamente:

- matriz_confusion.png
- arbol_decision.png
- reporte_clasificacion.txt
- predicciones_prueba.csv

Estas evidencias se utilizarán en el documento final y en el video de presentación.
