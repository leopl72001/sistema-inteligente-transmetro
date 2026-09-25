# Guion sugerido para el video - máximo 10 minutos

## 1. Presentación - 30 segundos

Hola, mi nombre es Julio Alberto Rebolledo Lambraño. En esta actividad desarrollé un sistema inteligente basado en conocimiento para calcular una ruta entre dos estaciones del sistema Transmetro de Barranquilla y Soledad. El proyecto utiliza reglas lógicas, una representación en grafo y los algoritmos de búsqueda de costo uniforme y A*.

## 2. Problema y base de conocimiento - 1:30 minutos

Abrir `src/base_conocimiento.py` y explicar:

- Se tomaron como referencia estaciones reales de la Troncal Murillo.
- Los tiempos son estimaciones académicas, no datos oficiales.
- Cada objeto `ReglaConexion` representa conocimiento del tipo: si existe una conexión entre A y B, se puede pasar de A a B con un costo.
- Al construir el grafo se aplica una regla adicional para permitir la conexión en ambos sentidos.

## 3. Estrategias de búsqueda - 2 minutos

Abrir `src/busqueda.py`.

Explicar que la búsqueda de costo uniforme explora primero las rutas de menor costo acumulado y que A* combina el costo recorrido con una estimación del costo restante.

```text
f(n) = g(n) + h(n)
```

## 4. Ejecución del programa - 2 minutos

En la terminal:

```bash
python main.py
```

Elegir como ejemplo Pacho Galán como origen y Atlántico como destino. Mostrar la ruta, el costo y la cantidad de nodos expandidos por ambos algoritmos.

## 5. Pruebas - 1:30 minutos

Ejecutar:

```bash
python -m unittest discover -v
```

Explicar que se validan seis aspectos: estaciones, bidireccionalidad, ruta óptima, coincidencia de costos, heurística y manejo de entradas inválidas.

## 6. Conclusión - 1 minuto

El proyecto demuestra cómo una base de conocimiento puede representar conexiones mediante reglas y cómo una estrategia heurística como A* puede orientar la búsqueda hacia el destino y reducir estados explorados en algunas consultas.
