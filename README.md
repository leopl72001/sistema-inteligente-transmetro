# Sistema inteligente de rutas - Transmetro

Proyecto académico para la Actividad 3 sobre **sistemas inteligentes basados en conocimiento**, representación mediante reglas lógicas y estrategias de búsqueda heurística.

## Objetivo

Construir en Python un sistema que represente conocimiento sobre conexiones entre estaciones y determine una ruta de costo mínimo entre un punto A y un punto B.

El caso de estudio utiliza estaciones reales de la **Troncal Murillo de Transmetro, Barranquilla/Soledad**. Los costos en minutos y las conexiones marcadas como `expreso_simulado` son valores definidos únicamente para la demostración académica y **no corresponden a tiempos ni servicios oficiales**.

## Conceptos implementados

- Base de conocimiento basada en reglas.
- Representación del transporte como grafo ponderado.
- Inferencia de conexiones bidireccionales.
- Búsqueda de costo uniforme.
- Búsqueda heurística A*.
- Función heurística basada en la posición relativa de las estaciones.
- Comparación de nodos expandidos por cada estrategia.
- Interfaz gráfica moderna desarrollada con Tkinter.
- Mapa visual de estaciones y animación de la ruta encontrada.
- Comparación gráfica entre costo uniforme y A*.
- Pruebas unitarias con `unittest`.

## Regla lógica usada

La idea general de cada conexión se puede expresar como:

```text
SI esta_en(Usuario, A) Y conecta(A, B) Y costo(A, B, C)
ENTONCES puede_moverse(Usuario, B, C)
```

Adicionalmente, para este modelo se aplica una regla de simetría:

```text
SI conecta(A, B)
ENTONCES conecta(B, A)
```

En Python estas reglas se representan mediante la clase `ReglaConexion` definida en `src/base_conocimiento.py`.

## Estructura

```text
sistema-inteligente-transmetro/
|-- interfaz.py
|-- main.py
|-- requirements.txt
|-- README.md
|-- src/
|   |-- __init__.py
|   |-- base_conocimiento.py
|   `-- busqueda.py
|-- tests/
|   |-- __init__.py
|   `-- test_sistema.py
`-- docs/
    |-- Informe_Pruebas.pdf
    |-- salida_prueba_1.txt
    `-- salida_prueba_2.txt
```

## Requisitos

- Python 3.10 o superior.
- No se requieren librerías externas.
- La interfaz gráfica utiliza **Tkinter**, incluido normalmente con Python.

## Ejecutar la interfaz gráfica

Desde la carpeta raíz del proyecto:

```bash
python interfaz.py
```

En Windows también puede utilizarse:

```bash
py interfaz.py
```

La interfaz permite:

- Seleccionar una estación de origen y destino.
- Intercambiar rápidamente las estaciones seleccionadas.
- Utilizar rutas de demostración preconfiguradas.
- Calcular la mejor ruta con costo uniforme y A*.
- Ver el costo estimado y la cantidad de nodos expandidos.
- Comparar visualmente la eficiencia de ambos algoritmos.
- Consultar el detalle de cada tramo.
- Visualizar la red de estaciones sobre un mapa esquemático.
- Ver la ruta resaltada progresivamente mediante una animación.
- Observar un punto animado recorriendo la ruta calculada.

## Ejecución por consola

La versión de consola continúa disponible con:

```bash
python main.py
```

El programa muestra las estaciones disponibles. Se selecciona el origen y el destino escribiendo sus números.

Ejemplo:

```text
Seleccione el numero de la estacion de origen: 2
Seleccione el numero de la estacion de destino: 9
```

El programa calcula la ruta con dos estrategias y presenta:

- Secuencia de estaciones.
- Costo estimado total.
- Tipo de cada tramo.
- Cantidad de nodos expandidos.
- Comparación entre costo uniforme y A*.

## Ejecutar pruebas

```bash
python -m unittest discover -v
```

Resultado esperado:

```text
Ran 6 tests
OK
```

## Archivos principales

### `src/base_conocimiento.py`
Contiene las estaciones, la representación de las reglas y la construcción del grafo.

### `src/busqueda.py`
Implementa búsqueda de costo uniforme, A*, heurística y reconstrucción de rutas.

### `interfaz.py`
Interfaz gráfica en Tkinter para seleccionar estaciones, calcular rutas, comparar algoritmos y visualizar el recorrido de forma animada.

### `main.py`
Interfaz de consola y comparación de resultados.

### `tests/test_sistema.py`
Valida la base de conocimiento, las reglas bidireccionales, la ruta óptima, la coincidencia entre algoritmos, la heurística y el manejo de estaciones inválidas.

## Fuente del caso de estudio

Transmetro S.A.S. - sitio oficial: https://transmetro.gov.co/

La página oficial lista las estaciones de la Troncal Murillo, entre ellas Portal de Soledad, Pacho Galán, Pedro Ramayá Beltrán, Joaquín Barrios Polo, Buenos Aires, La Ocho, La Catorce, La Veintiuna, Atlántico, Chiquinquirá y La Arenosa.
