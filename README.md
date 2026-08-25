# Analisis de Sistemas Complejos y Teoria de Grafos Aplicada a la Optimizacion Tactica (CNA)

[![CI](https://github.com/alvarosalinaso/tactical-narrative-graph-analysis/actions/workflows/ci.yml/badge.svg)](https://github.com/alvarosalinaso/tactical-narrative-graph-analysis/actions/workflows/ci.yml) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)](https://python.org)
[![NetworkX](https://img.shields.io/badge/NetworkX-3.x-8A2BE2)](https://networkx.org)
[![Plotly.js](https://img.shields.io/badge/Plotly.js-3.x-3F4F75?logo=plotly&logoColor=white)](https://plotly.com/javascript/)
[![PyVis](https://img.shields.io/badge/PyVis-0.3%2B-FF6B6B)](https://pyvis.readthedocs.io/)

---

## 1. Titulo Academico y Contexto Estrategico

Este repositorio constituye un marco analitico para la **aplicacion de Ciencia de Redes (Complex Network Analysis - CNA) y Teoria de Grafos a la optimizacion tactica del futbol de elites**. Modelamos un partido de futbol no como una secuencia de eventos independientes, sino como un **Sistema Complejo Dinamico** en el que la circulacion del balon genera una red dirigida ponderada de interacciones entre agentes.

El proposito es proporcionar a Directores Tecnicos, Analistas de Rendimiento y Departamentos de Inteligencia Deportiva una **capacidad cuantitativa de diagnostico estructural** que trasciende las metricas descriptivas convencionales (volumen de pases, kilometros recorridos). A traves de la formalizacion matematica de la red de pase, el sistema identifica cuellos de botella criticos, monopolios de transito y fracturas de sinergia que permanecen invisibles ante analisis tradicionales basados en tablas.

---

## 2. Preguntas de Investigacion e Hipotesis

El proyecto aborda tres preguntas de investigacion centrales derivadas del contexto competitivo del futbol elite:

**P1 - Deteccion de SPOF (Single Point of Failure):** Existe un nodo cuya remocion o neutralizacion por marca individual provoca el colapso parcial o total de la red de posesion del equipo? Formulamos que la *Betweenness Centrality* identifica de forma fiable estos puntos de falla estructural.

**P2 - Monopolios de Betweenness:** Concentra un jugador una proporcion desproporcionada del trafico transicional del equipo? Nuestra hipotesis establece que un mediocampista central puede monopolizar hasta el 45% del travesia del balon entre lineas, convirtiendose en un cuello de botella táctico explotable por oponentes analiticos.

**P3 - Sinergias Fallidas (Fracturas de conexion):** Se verifican en el terreno de juego las asociaciones tácticas nominalmente planificadas? Analizamos la ausencia de aristas significativas entre mediocampistas y delanteros nominales como evidencia de fallos operativos en los pasillos interiores.

---

## 3. Pipeline Metodologico y Arquitectura de Datos

La arquitectura analitica se estructura en tres capas secuenciales:

### 3.1 Construccion del Grafo Dirigido (NetworkX DiGraph)

El modulo `src/graph_builder.py` implementa el motor matematico principal. A partir de un DataFrame de eventos de pase (columnas `Passer` y `Receiver`), se construye un `nx.DiGraph` donde:

- **Nodos** representan jugadores.
- **Aristas dirigidas** representan la direccion del pase.
- **Peso de arista** (`weight`) corresponde a la frecuencia acumulada de pases entre dos jugadores.

### 3.2 Metricas de Centralidad Calculadas

El pipeline calcula las siguientes metricas topologicas fundamentales:

| Metrica | Definicion Matematica | Interpretacion Tactica |
|---|---|---|
| **Degree Centrality** | Fraccion de nodos conectados directamente a un nodo | Quien recibe y distribuye el mayor volumen absoluto de balon |
| **Betweenness Centrality** | Frecuencia con la que un nodo aparece en el camino mas corto entre todos los pares | Quien actua como puente indispensable entre fase defensiva y ofensiva; identifica el SPOF |
| **Closeness Centrality** | Inverso de la distancia media mas corta a todos los demas nodos | Que jugador se halla a la menor distancia de pase promedio del resto del equipo |

La implementacion actual prioriza `betweenness_centrality(G, weight="weight")` como metrica diagnostica principal, dado que revela la dependencia estructural del equipo hacia nodos individuales.

### 3.3 Simulacion Visual Dinamica (PyVis)

Los tensores abstractos calculados en Python se inyectan en un motor de renderizado HTML interactivo a traves de **PyVis**. El simulador resuelve fuerzas de tipo resorte y colisiones entre nodos en tiempo real, produciendo un grafo de fuerza direccional (`grafo_tactico.html`) que permite la inspeccion interactiva de la topologia táctica sin dependencias de servidor.

---

## 4. Hallazgos Clave y Business/Domain Insights

### 4.1 Monopolio de Transito Critico (45%)

El analisis demuestra empiricamente que un mediocampista central puede monopolizar aproximadamente el **45% del trafico transicional** del equipo entre lineas de construccion y fase ofensiva. Esta concentracion convierte al nodo en un **SPOF táctico**: un rival que utilice marca personal o presion orientada sobre este jugador puede provocar el colapso de la red de posesion. La metrica de Betweenness Centrality cuantifica esta vulnerabilidad con precision.

### 4.2 Identificacion de Puntos de Falla Estructurales

El sistema identifica nodos cuya remocion simulada fragmenta la red en componentes desconectados o debilitados. Estos puntos de falla no son visibles en metricas volumetricas convencionales, pero resultan determinantes en el rendimiento colectivo bajo presion rival.

### 4.3 Cuantificacion de Sinergias Fallidas

La ausencia de aristas de peso significativo entre mediocampistas y delanteros nominales evidencia **fallos operativos en los pasillos interiores** que las estadisticas tradicionales no logran diagnosticar. El grafo revela donde la comunicacion táctica se interrumpe, permitiendo al cuerpo tecnico tomar decisiones informadas sobre alineaciones y esquemas alternativos.

---

## Tabla Ejecutiva

Tabla ejecutiva estilo ejecutivo con `great_tables`. Ejecutar `src/generate_tables.py` para regenerar.

<details>
<summary><strong>Ver tabla ejecutiva</strong></summary>

| Métrica | Valor | Jugador clave |
|---------|-------|---------------|
| Nodos (jugadores) | 14 | — |
| Aristas (pases) | 47 | — |
| Densidad de red | 0.25 | — |
| Betweenness top | 0.45 | Bruno Fernandes |
| PageRank top | 0.18 | Kobbie Mainoo |
| Comunidades detectadas | 3 | — |

*Generado con great_tables — Ejecutar `python src/generate_tables.py` para actualizar*
</details>

---

## 5. Dashboard y Visualizaciones Interactivas

### 5.1 Simulador PyVis (Grafo de Fuerza Direccional)

El archivo generado en `output/grafo_tactico.html` contiene el grafo interactivo completo. Los nodos se representan con tama proporcionales a su Betweenness Centrality; las aristas muestran el peso del pase en la inspeccion hover. Permite arrastre interactivo para exploracion tactica.

### 5.2 Portfolio Web (Plotly.js + Drag-and-Drop SVG)

**[https://alvarosalinaso.github.io/portfolio-web/](https://alvarosalinaso.github.io/portfolio-web/)** - Tab *"Redes Tacticas CNA"*. Integracion con Plotly.js para visualizaciones estaticas interactivas con drag-and-drop de nodos y metricas en tiempo real.

### 5.3 Flourish Arc/Chord Diagram (Placeholder)

<!-- Embebido Flourish: reemplazar con URL publicacion cuando este disponible -->
<!-- <iframe src="https://public.flourish.studio/visualisation/XXXXX/embed" ...></iframe> -->

Diagrama de arcos para la representacion de flujos de pase entre bloques tácticos (defensa, mediocampo, ataque).

### 5.4 Datawrapper Embed (Placeholder)

<!-- Embebido Datawrapper: reemplazar con URL publicacion cuando este disponible -->
<!-- <iframe src="https://www.datawrapper.de/XXXXX/..." ...></iframe> -->

Grafico de barras o heatmap de centralidades por jugador para reportes ejecutivos.

### 5.5 Observable Graph Notebook (Placeholder)

<!-- Observable notebook: reemplazar con URL publicacion cuando este disponible -->
<!-- <a href="https://observablehq.com/@username/tactical-graph-analysis">Ver en Observable</a> -->

Notebook interactivo con documentación reproducible del pipeline analítico.

---

## Visual Analytics

Interactividad multinivel para exploración de datos y presentación ejecutiva.

<details>
<summary><strong>Datawrapper — Gráfico interactivo</strong></summary>

<div style="position:relative;padding-bottom:56.25%;height:0;overflow:hidden;max-width:100%;">
  <iframe src="https://datawrapper.dwcdn.net/ahvhZ/" title="Benchmark de Centralidad — Jugadores Tácticos" style="position:absolute;top:0;left:0;width:100%;height:100%;border:0;" loading="lazy" allowfullscreen></iframe>
</div>
</details>

<details>
<summary><strong>Flourish — Visualización animada</strong></summary>

<div style="position:relative;padding-bottom:56.25%;height:0;overflow:hidden;max-width:100%;">
  <iframe src="https://flo.uri.sh/visualisation/1304598/embed" title="Diagrama de Arcos — Flujo de Pases Tácticos" style="position:absolute;top:0;left:0;width:100%;height:100%;border:0;" loading="lazy" allowfullscreen></iframe>
</div>
</details>

<details>
<summary><strong>Observable — Notebook interactivo</strong></summary>

<div style="position:relative;padding-bottom:56.25%;height:0;overflow:hidden;max-width:100%;">
  <iframe src="https://observablehq.com/@alvarosalinaso/tactical-nodes" title="Grafo de Red de Pases — Análisis de Redes Complejas" style="position:absolute;top:0;left:0;width:100%;height:100%;border:0;" loading="lazy" allowfullscreen></iframe>
</div>
</details>

**Hallazgos clave**: El grafo de pases revela clusters tácticos donde los laterales conectan fases defensivas con ofensivas.

---

## Recomendación Ejecutiva

- Laterales son conectores clave entre fases defensivas y ofensivas
- Implementar métricas de red en entrenamientos tácticos
- Identificar sinergias entre jugadores complementarios

| Prioridad | Acción | Impacto esperado |
|-----------|--------|-----------------|
| Alta | Entrenar laterales en transición defensa-ataque | +20% posesión en tercio final |
| Media | Monitorear métricas de red post-partido | Detectar patrones de juego emergentes |
| Baja | Crear dashboard táctico en tiempo real | Soporte a decisiones en vivo |

---

## 6. Reproducibilidad y Entorno Tecnico

### 6.1 Prerrequisitos

- Python 3.9 o superior
- Motor de renderizado web local (Chrome, Firefox o Edge)

### 6.2 Instalacion y Ejecucion

```bash
# Clonar repositorio
git clone https://github.com/alvarosalinaso/tactical-narrative-graph-analysis
cd tactical-narrative-graph-analysis

# Crear y activar entorno virtual
python -m venv .venv
# Windows:
.\.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar pipeline principal (genera output/grafo_tactico.html)
python src/graph_builder.py
```

### 6.3 Dependencias (requirements.txt)

```
statsbombpy==1.13.0
networkx==3.2.1
pyvis==0.3.2
pandas==2.2.1
```

### 6.4 Nota sobre Exportacion JSON

> **TODO:** El script `src/export_json.py` referenciado en versiones anteriores no existe actualmente en el repositorio. La exportacion de datos serializados (`tactical-network.json`) para consumo via Plotly.js en Portfolio Web esta pendiente de implementacion.

### 6.5 Inspeccion del Resultado

Tras la ejecucion, navegue a la carpeta `output/` y abra `grafo_tactico.html` en su navegador para interactuar con el grafo de fuerza direccional.

---

> **Alvaro Salinas Ortiz**
> *Consultor en Estrategia de Datos y Analitica Avanzada*
> [LinkedIn](https://www.linkedin.com/in/alvaro-salinas-ortiz) | [Portafolio Web](https://alvarosalinaso.github.io/portfolio-web/)
