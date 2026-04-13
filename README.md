# Technical Tactical Graph (Compley Network Analysis)

Proyecto de arquitectura de datos pura (Data Strategy). Este repositorio salda la brecha entre ver un partido de fútbol como una "serie de eventos aislados" para interpretarlo algorítmicamente como un **Sistema Complejo**.

A través de la *Teoría de Grafos* y el *Análisis de Redes* (Complex Network Analysis - CNA) podemos abstraer el partido y usar Python puro para encontrar cuellos de botella en la información (quién monopoliza el balón), calcular *Betweenness Centrality* (qué jugador es el punto de falla del equipo si recibe marca personal), y renderizar estas interacciones en un espacio digital 3D o 2D navegable.

## Naturaleza Tecnológica

*   **Matemática de Nodos (`NetworkX`):** Procesador de red central. Cuantifica aristas y tensores.
*   **Motor Visual Físico (`PyVis`):** Inyecta los cálculos abstractos de Python y los proyecta a un simulador de colisiones y gravedades dinámico en formato `HTML`.

## Estructura

```text
/tactical-narrative-graph-analysis/
├── src/
│   └── graph_builder.py       # Núcleo de cálculo centralizado (NetworkX)
├── output/
│   └── grafo_tactico.html     # (Auto-generado) La simulación física
```

## Setup de Pruebas

```bash
git clone https://github.com/alvarosalinaso/tactical-narrative-graph-analysis
cd tactical-narrative-graph-analysis
pip install -r requirements.txt

# Disparo del motor y generación
python src/graph_builder.py
```

> Al ejecutar el script en tu computadora, navegarás en la carpeta `/output`. Dale doble click al archivo `HTML` y arrastra las bolas (Nodos Player) para ver el nivel de inmersión y cálculo en tiempo real del que eres capaz de desarrollar.

> **Álvaro Salinas Ortiz** | Advanced Data Strategy & Network Operations
