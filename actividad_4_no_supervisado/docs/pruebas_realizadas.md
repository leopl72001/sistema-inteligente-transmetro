# Pruebas realizadas al componente no supervisado

## Pruebas automatizadas

Se desarrollaron seis pruebas con `unittest`:

1. El dataset contiene exactamente 420 registros.
2. No existen las columnas `estado_servicio` ni `demora_min`.
3. Todas las variables requeridas por el modelo están presentes.
4. K-Means genera exactamente tres clusters.
5. Los 420 registros reciben una asignación de cluster.
6. Los tres centroides tienen la misma cantidad de dimensiones que las variables utilizadas.

Comando de ejecución:

    python -m unittest discover -s actividad_4_no_supervisado/tests -p "test_*.py" -v

Resultado verificado:

    Ran 6 tests
    OK

## Prueba del modelo

El modelo K-Means se ejecutó con:

- k = 3 clusters.
- semilla = 42.
- máximo de 100 iteraciones.
- variables estandarizadas antes del agrupamiento.

Resultados verificados:

- Registros: 420.
- Iteraciones hasta convergencia: 7.
- Inercia: 1478.29.
- Silhouette promedio: 0.268.

Distribución de los grupos:

- Cluster 1: 116 registros.
- Cluster 2: 102 registros.
- Cluster 3: 202 registros.

Centroides en escala original:

| Indicador | Cluster 1 | Cluster 2 | Cluster 3 |
|---|---:|---:|---:|
| Número de paradas promedio | 2.84 | 7.33 | 2.67 |
| Hora promedio | 13.25 | 13.45 | 14.27 |
| Proporción hora pico | 1.00 | 0.33 | 0.00 |
| Pasajeros promedio | 86.78 | 59.20 | 50.39 |
| Proporción lluvia | 0.23 | 0.27 | 0.27 |
| Tiempo base promedio | 11.40 | 23.07 | 10.95 |

## Interpretación

Después del agrupamiento, los clusters pueden interpretarse de forma descriptiva:

- Cluster 1: recorridos cortos con alta demanda asociados principalmente a horas pico.
- Cluster 2: recorridos largos con demanda media y mayor tiempo base.
- Cluster 3: recorridos cortos, fuera de hora pico y con menor demanda.

Estos nombres no fueron entregados al algoritmo antes del entrenamiento. Se asignan únicamente después de observar los centroides obtenidos.

## Evidencias generadas

La ejecución crea:

- `clusters.csv`
- `resumen_clusters.txt`
- `interpretacion_clusters.txt`
- `clusters.svg`
