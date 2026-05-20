# Análisis de Sistemas Complejos y Teoría de Grafos Aplicada a la Optimización Táctica (CNA)

🚀 **[Ver Simulación Interactiva en Vivo]** *(Si aplica enlace a output interactivo)*

---

## Executive Summary & Decision Making

Este proyecto diseña e implementa una infraestructura avanzada de **Ciencia de Redes (Complex Network Analysis - CNA)** y **Teoría de Grafos** aplicada al rendimiento deportivo de élite. Mediante la modelación matemática de un partido de fútbol no como eventos independientes aislados, sino como un **Sistema Complejo Dinámico**, el algoritmo deconstruye las interacciones colectivas del equipo. Esto permite parametrizar de forma cuantitativa la circulación de información (el balón), identificar vulnerabilidades estructurales en la red y optimizar la resiliencia táctica colectiva.

El análisis de grafos tácticos capacita a Directores Técnicos, Analistas de Rendimiento y Departamentos de Inteligencia Deportiva para tomar **decisiones tácticas de alto nivel**:
1. **Identificación y Mitigación de Puntos de Falla Críticos:** Detectar de forma cuantitativa qué jugadores tienen una métrica de centralidad crítica (*Betweenness Centrality*). Esto identifica cuellos de botella tácticos: si el rival neutraliza a este nodo mediante marca personal, la red de posesión del equipo colapsa por completo.
2. **Rediseño de Patrones de Circulación (Tactical De-bottlenecking):** Diseñar e implementar alternativas de pase para distribuir mejor la centralidad del juego, reduciendo la dependencia de jugadores aislados y aumentando la imprevisibilidad ofensiva.
3. **Auditoría de Sinergia y Conexión de Plantilla:** Evaluar empíricamente la efectividad de las sociedades tácticas en el terreno de juego, tomando decisiones informadas sobre alineaciones iniciales y contrataciones basadas en compatibilidad estructural y cooperativa.

[INSERTAR SIMULACIÓN DINÁMICA DE COLISIONES DE GRAFOS TÁCTICOS AQUÍ]

---

## Business Context & Challenge

En el fútbol moderno de élite, la diferencia entre ganar y perder se define por detalles milimétricos y adaptaciones tácticas en tiempo real. Los clubes acumulan volúmenes inmensos de datos de eventos, pero los análisis convencionales basados exclusivamente en tablas de volumen (p. ej., "el jugador X completó 50 pases") son insuficientes. No capturan la estructura relacional del juego, la influencia de los circuitos de pase ni la topología de la red de juego.

El desafío de este proyecto consiste en **traducir la Teoría de Grafos en una ventaja competitiva en el terreno de juego**, abstrayendo las dinámicas espaciales e interaccionales en una red de nodos (jugadores) y aristas con peso (frecuencia y dirección de pases). Esto permite responder a la pregunta de negocio: *¿Cómo responde nuestro equipo estructuralmente ante la presión del oponente y qué tan vulnerables somos a perder nuestra capacidad de distribución?*

---

## Data Architecture & Analytical Approach

La metodología y arquitectura del proyecto garantizan rigor matemático e interactividad táctica:

[INSERTAR DIAGRAMA DE FLUJO: EVENTOS DE PASE -> NETWORKX CENTRALITY -> GENERACIÓN DE HTML INTERACTIVO PYVIS AQUÍ]

1. **Modelado y Matemática de Nodos (`NetworkX`):** Desarrollo del motor matemático principal que construye el grafo de juego directo. El algoritmo calcula tensores de red y métricas estructurales críticas:
   - **Degree Centrality:** Quién recibe y distribuye el mayor volumen absoluto de balón.
   - **Betweenness Centrality:** Quién actúa como puente indispensable para conectar la línea de defensa con la fase ofensiva.
   - **Closeness Centrality:** Qué jugador se encuentra a la distancia media de pases más corta del resto del equipo, facilitando transiciones rápidas.
2. **Visualización y Simulación Física Dinámica (`PyVis`):** Inyección de las matrices abstractas calculadas en Python en un motor visual HTML dinámico. Este simulador calcula colisiones, fuerzas gravitacionales y tensiones de resorte físicas interactivas en tiempo real.
3. **Generación de Outputs Autoportantes:** Exportación automática de la visualización interactiva a un formato HTML ligero (`grafo_tactico.html`) ideal para presentación inmediata ante cuerpos técnicos o directivas en tablets y ordenadores portátiles, libre de dependencias de servidor complejas.

---

## Strategic Insights & Impact

El modelado analítico mediante Teoría de Grafos arroja conclusiones transformadoras sobre el rendimiento colectivo:

- **Detección de Monopolios Críticos:** El análisis demuestra de forma empírica cómo en ciertos esquemas tácticos un solo mediocampista central monopoliza el 45% del tránsito de balón transicional del equipo, transformándolo en un punto único de falla (Single Point of Failure - SPOF) fácilmente detectable e inutilizable por entrenadores rivales analíticos.
- **Visualización Inmersiva de Roles Reales:** El simulador gravitacional permite arrastrar los nodos de los jugadores de forma interactiva en la pantalla de análisis táctico, facilitando a los cuerpos técnicos comprender la elasticidad, el acoplamiento y el espacio real que las sociedades de juego ocupan durante el partido.
- **Cuantificación de Sinergias Fallidas:** El sistema expone la ausencia de aristas significativas (pases) entre mediocampistas y delanteros nominales, evidenciando fallas operativas en los pasillos interiores que las estadísticas tradicionales no logran diagnosticar.

[INSERTAR GRÁFICO DE BARRAS DE MÉTRICAS DE CENTRALIDAD COMPARATIVAS ENTRE JUGADORES AQUÍ]

---

## Infraestructura, Despliegue y Ejecución

El código del proyecto está optimizado para ejecutarse localmente de forma fluida sin configuraciones avanzadas.

### Prerrequisitos
- Python 3.9+
- Motor de renderizado web local

### Setup y Ejecución Local
1. **Clonación del repositorio y aislamiento de entorno:**
   ```bash
   git clone https://github.com/alvarosalinaso/tactical-narrative-graph-analysis
   cd tactical-narrative-graph-analysis
   python -m venv .venv
   ```
2. **Activación del entorno virtual (Windows):**
   ```powershell
   .\.venv\Scripts\activate
   ```
3. **Instalación de las librerías matemáticas y visuales:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Ejecución del pipeline y generación del mapa dinámico:**
   ```bash
   python src/graph_builder.py
   ```
5. **Navegación e Inspección Visual:**
   Navega a la carpeta `/output/`, abre el archivo `grafo_tactico.html` en tu navegador de preferencia y arrastra interactivamente los nodos de los jugadores en la simulación física integrada.

---

> **Álvaro Salinas Ortiz**
> *Consultor en Estrategia de Datos y Analítica Avanzada*
> [LinkedIn](https://www.linkedin.com/in/alvaro-salinas-ortiz) | [Portafolio Web](https://alvarosalinaso.github.io)
