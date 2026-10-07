# Descripcion de los datos - Actividad 5

## Contexto

El proyecto continúa el caso académico de rutas de Transmetro trabajado en las actividades anteriores. Para esta fase se requiere un modelo de aprendizaje supervisado. Como no se dispone dentro del proyecto de una fuente histórica oficial con todas las variables necesarias para entrenamiento, se construyó un dataset sintético de 420 observaciones.

Los nombres de estaciones corresponden al corredor utilizado en el proyecto anterior. Los valores de demanda, lluvia, incidentes, tiempos base y estado del servicio son simulados y se usan exclusivamente con fines académicos.

## Variable objetivo

estado_servicio es la etiqueta que aprende a predecir el árbol de decisión. Tiene tres categorías:

- Normal: operación sin afectación significativa.
- Demorado: operación con condiciones que aumentan el tiempo o complejidad del recorrido.
- Critico: condición de mayor afectación, especialmente asociada a incidentes y otras condiciones de alta demanda.

## Diccionario de datos

| Variable | Tipo | Descripcion | Uso en el modelo |
|---|---|---|---|
| id | Entero | Identificador del registro | No |
| origen | Categorica | Estacion de salida | Si |
| destino | Categorica | Estacion de llegada | Si |
| numero_paradas | Entero | Distancia relativa entre estaciones | Si |
| hora | Entero | Hora del registro, de 5 a 22 | Si |
| hora_pico | Binaria | 1 si corresponde a franja pico | Si |
| tipo_dia | Categorica | Habil, Sabado o Domingo | Si |
| pasajeros | Entero | Demanda simulada de pasajeros | Si |
| lluvia | Binaria | Presencia simulada de lluvia | Si |
| incidente | Binaria | Presencia simulada de incidente | Si |
| tiempo_base_min | Decimal | Tiempo base estimado para el recorrido | Si |
| demora_min | Decimal | Demora observada simulada | No |
| estado_servicio | Categorica | Normal, Demorado o Critico | Objetivo |

## Consideracion sobre fuga de informacion

La columna demora_min se conserva para describir cada observación, pero no se usa como variable predictora. Utilizarla directamente haría demasiado fácil la clasificación y produciría fuga de información, porque la demora observada está muy relacionada con la etiqueta que se desea predecir.

## Generacion

El archivo fue construido con una semilla fija para que pueda reproducirse. El script src/generar_dataset.py vuelve a producir el conjunto con las mismas reglas académicas. Se añadió aproximadamente un 5 % de variación en las etiquetas para evitar un conjunto artificialmente perfecto.
