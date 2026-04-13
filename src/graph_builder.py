import pandas as pd
import networkx as nx
from pyvis.network import Network
import os

# Simularemos un generador offline primero para asegurar estabilidad inmediata.
# En producción, usaríamos `from statsbombpy import sb` 
# y haríamos: sb.events(match_id=3750201)

def build_graph(data: pd.DataFrame) -> nx.DiGraph:
    """Extrae las conexiones dirigidas de Pases y crea el Grafo Matemático"""
    G = nx.DiGraph()
    
    # Agregar Nodos y bordes con peso (Weight = N° de Pases)
    for index, row in data.iterrows():
        source = row['Passer']
        target = row['Receiver']
        
        if G.has_edge(source, target):
            G[source][target]['weight'] += 1
        else:
            G.add_edge(source, target, weight=1)
            
    return G

def analyze_and_visualize(G: nx.DiGraph, output_filename="grafo_tactico.html"):
    """
    Calcula Betweenness Centrality (El dictador o 'broker' táctico del equipo)
    y renderiza el mapa en HTML interactivo
    """
    # 1. Análisis de centralidad (Matemática Pura)
    centrality = nx.betweenness_centrality(G, weight='weight')
    
    # 2. Configurar motor visual PyVis
    net = Network(height="600px", width="100%", bgcolor="#222222", font_color="white", directed=True)
    
    # Transformar a formato visual
    for node in G.nodes():
        # El tamaño del jugador en el mapa dependerá de cuánto es el 'puente' táctico
        size = centrality.get(node, 0.01) * 200 + 10 
        net.add_node(node, label=node, title=f"Betweenness: {centrality.get(node, 0.01):.2f}", size=size)
        
    for source, target, data in G.edges(data=True):
        weight = data['weight']
        net.add_edge(source, target, value=weight, title=f"{weight} pases")
        
    # Guardar en local (Se puede abrir en cualquier navegador web)
    os.makedirs("output", exist_ok=True)
    out_path = os.path.join("output", output_filename)
    net.write_html(out_path)
    print(f"Grafo interactivo renderizado con éxito en: {out_path}")

if __name__ == "__main__":
    # Generamos un dataset esqueleto con base en tus propias estadísticas de passing.csv del United
    # Esto asegura de que corra a la primera (Plug-and-play)
    mock_data = pd.DataFrame([
        {"Passer": "Onana", "Receiver": "Martinez"},
        {"Passer": "Onana", "Receiver": "Dalot"},
        {"Passer": "Martinez", "Receiver": "Bruno Fernandes"},
        {"Passer": "Martinez", "Receiver": "Mainoo"},
        {"Passer": "Dalot", "Receiver": "Bruno Fernandes"},
        {"Passer": "Mainoo", "Receiver": "Bruno Fernandes"},
        {"Passer": "Bruno Fernandes", "Receiver": "Garnacho"},
        {"Passer": "Bruno Fernandes", "Receiver": "Garnacho"},
        {"Passer": "Bruno Fernandes", "Receiver": "Hojlund"},
        {"Passer": "Garnacho", "Receiver": "Hojlund"},
    ])
    
    grafo = build_graph(mock_data)
    analyze_and_visualize(grafo)
