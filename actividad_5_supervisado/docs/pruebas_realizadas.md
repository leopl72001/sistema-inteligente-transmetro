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

## Prueba del modelo

El dataset se divide de manera estratificada en 75 % para entrenamiento y 25 % para prueba, con random_state=42. Esto produce 315 registros de entrenamiento y 105 registros de prueba.

El clasificador utilizado es DecisionTreeClassifier con profundidad máxima 5 y mínimo de 4 muestras por hoja.

Con el dataset incluido en el repositorio se obtiene aproximadamente:

- Accuracy: 93.33 %
- Matriz de confusión, en el orden Normal / Demorado / Critico:
  - Normal: 70 correctos.
  - Demorado: 21 correctos y 4 clasificados como Normal.
  - Critico: 7 correctos y 3 clasificados como Normal.

El resultado no es perfecto, lo cual es coherente con el pequeño porcentaje de variación introducido en las etiquetas del dataset sintético.

## Archivos generados al ejecutar el modelo

Al ejecutar:

    python actividad_5_supervisado/src/modelo_supervisado.py

se crean automáticamente dentro de resultados:

- matriz_confusion.png
- arbol_decision.png
- reporte_clasificacion.txt
- predicciones_prueba.csv

Estos archivos sirven como evidencia para el documento final y el video.
