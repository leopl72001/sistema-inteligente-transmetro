# Actividad 5 - Metodos supervisados

Continuación del proyecto académico de transporte masivo desarrollado con Transmetro como caso de estudio.

## Objetivo

Desarrollar un modelo de aprendizaje supervisado que clasifique el estado de un recorrido como Normal, Demorado o Critico mediante un árbol de decisión.

## Compatibilidad

La versión actual del modelo está implementada con la biblioteca estándar de Python y no depende de pandas, scikit-learn ni matplotlib. Esto permite ejecutarla incluso en equipos donde las políticas de seguridad de Windows bloquean extensiones binarias instaladas dentro de entornos virtuales.

## Estructura

    actividad_5_supervisado/
    ├── data/
    │   └── datos_transmetro_supervisado.csv
    ├── src/
    │   ├── generar_dataset.py
    │   └── modelo_supervisado.py
    ├── tests/
    │   └── test_modelo.py
    ├── docs/
    │   ├── descripcion_datos.md
    │   ├── pruebas_realizadas.md
    │   └── mapa_conceptual.md
    ├── resultados/
    │   └── README.md
    └── requirements.txt

## Ejecutar modelo

Desde la raíz del repositorio:

    python actividad_5_supervisado/src/modelo_supervisado.py

El programa entrena un árbol de decisión con profundidad máxima 5, divide los datos de forma estratificada en 75 % entrenamiento y 25 % prueba, calcula las métricas y genera:

- reporte_clasificacion.txt
- predicciones_prueba.csv
- matriz_confusion.svg
- arbol_decision.svg

## Ejecutar pruebas

    python -m unittest actividad_5_supervisado.tests.test_modelo -v

## Dataset

El conjunto contiene 420 registros sintéticos. Los datos fueron creados con fines académicos porque el proyecto no dispone de una fuente histórica oficial con todas las variables requeridas.

La variable demora_min es descriptiva y no se utiliza para entrenar el modelo para evitar fuga de información.

## Resultado de referencia

Con la configuración incluida y semilla 42, el modelo obtiene 93.33 % de accuracy sobre 105 registros de prueba.

## Repositorio

https://github.com/leopl72001/sistema-inteligente-transmetro

## Video

Agregar aquí el enlace final del video antes de entregar.
