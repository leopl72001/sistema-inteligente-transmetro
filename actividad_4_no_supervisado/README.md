# Actividad 4 - Métodos de aprendizaje no supervisado

Continuación del proyecto académico de transporte masivo desarrollado con Transmetro como caso de estudio.

## Objetivo

Aplicar aprendizaje no supervisado mediante K-Means para descubrir perfiles de recorridos con características operativas similares, sin utilizar una variable objetivo previamente etiquetada.

## Estructura

    actividad_4_no_supervisado/
    ├── data/
    │   └── datos_transmetro_no_supervisado.csv
    ├── src/
    │   └── modelo_no_supervisado.py
    ├── tests/
    │   └── test_modelo_no_supervisado.py
    ├── docs/
    │   ├── descripcion_datos.md
    │   └── pruebas_realizadas.md
    ├── resultados/
    └── requirements.txt

## Requisitos

No requiere librerías externas. Funciona con Python estándar.

## Ejecutar el modelo

Desde la raíz del repositorio:

    python actividad_4_no_supervisado/src/modelo_no_supervisado.py

El programa genera automáticamente:

- clusters.csv
- resumen_clusters.txt
- interpretacion_clusters.txt
- clusters.svg

## Ejecutar las pruebas

    python -m unittest discover -s actividad_4_no_supervisado/tests -p "test_*.py" -v

## Datos

El dataset contiene 420 registros sintéticos y no incluye una variable objetivo. El modelo utiliza:

- numero_paradas
- hora
- hora_pico
- pasajeros
- lluvia
- tiempo_base_min

Las variables se estandarizan antes de calcular distancias.

## Resultados de referencia

- 420 registros.
- 3 clusters.
- 7 iteraciones hasta convergencia.
- Inercia: 1478.29.
- Silhouette promedio: 0.268.
- Tamaños de clusters: 116, 102 y 202 registros.

## Repositorio

https://github.com/leopl72001/sistema-inteligente-transmetro

## Video

Agregar aquí el enlace del video antes de la entrega final.
