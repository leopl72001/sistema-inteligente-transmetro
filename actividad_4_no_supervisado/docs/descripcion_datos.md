# Descripción de los datos - Actividad 4

## Contexto

La actividad continúa el proyecto académico de transporte masivo desarrollado con Transmetro como caso de estudio. Para aplicar aprendizaje no supervisado se preparó un dataset sin variable objetivo, de modo que el algoritmo pueda descubrir grupos a partir de similitudes entre los registros.

El archivo contiene 420 observaciones derivadas del conjunto sintético utilizado en la actividad anterior. Los nombres de estaciones corresponden al caso de estudio del proyecto, mientras que los valores operativos son simulados con fines académicos.

## Fuente

No se dispone dentro del proyecto de una fuente histórica oficial que reúna simultáneamente demanda, horarios, lluvia, incidentes, número de paradas y tiempos de recorrido. Por esta razón se utiliza una muestra sintética reproducible.

A diferencia de la actividad supervisada, se eliminaron las columnas `estado_servicio` y `demora_min`. Esto evita suministrar al algoritmo una clasificación previa y mantiene el carácter no supervisado del ejercicio.

## Variables del archivo

| Variable | Tipo | Descripción | Uso en K-Means |
|---|---|---|---|
| id | Entero | Identificador del registro | No |
| origen | Categórica | Estación de origen | Metadato |
| destino | Categórica | Estación de destino | Metadato |
| numero_paradas | Numérica | Distancia relativa entre estaciones | Sí |
| hora | Numérica | Hora simulada del recorrido | Sí |
| hora_pico | Binaria | Indica si corresponde a hora pico | Sí |
| tipo_dia | Categórica | Hábil, sábado o domingo | Metadato |
| pasajeros | Numérica | Demanda estimada de pasajeros | Sí |
| lluvia | Binaria | Presencia simulada de lluvia | Sí |
| incidente | Binaria | Presencia simulada de incidente | No en el modelo principal |
| tiempo_base_min | Numérica | Tiempo base estimado | Sí |

## Variables utilizadas para agrupar

El modelo trabaja con seis variables numéricas:

- numero_paradas
- hora
- hora_pico
- pasajeros
- lluvia
- tiempo_base_min

Antes de aplicar K-Means, estas variables se estandarizan utilizando media y desviación estándar. Esto evita que variables con escalas mayores, como pasajeros, dominen el cálculo de distancias.

## Variable objetivo

No existe variable objetivo. El algoritmo no recibe etiquetas como Normal, Demorado o Crítico. Los grupos aparecen como resultado del análisis de similitud entre registros.
