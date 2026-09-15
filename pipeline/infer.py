import networkx as nx
from typing import List, Tuple

def build_relationship_graph(extractions: list) -> nx.DiGraph:
    """Converts extraction triples into a directed graph."""
    G = nx.DiGraph()
    for item in extractions:
        if "subject" in item and "action" in item and "object" in item:
            # Add edge labeled with the action (e.g., "identify" → "user profile")
            G.add_edge(item["subject"], item["object"], action=item["action"])
    return G

def infer_transitive_relationships(G: nx.DiGraph, max_depth: int = 2) -> list:
    """Finds implied relationships via paths (e.g., A→B→C implies A→C)."""
    inferred = []
    for source in G.nodes():
        for target in G.nodes():
            if source == target:
                continue
            try:
                # Find shortest path (if exists and within depth limit)
                path = nx.shortest_path(G, source, target)
                if 2 <= len(path) <= max_depth + 1:  # Path length = nodes in path
                    # Infer relationship: subject (path[0]) -> object (path[-1])
                    # Action is concatenation of intermediate actions (simplified)
                    actions = [G[path[i]][path[i+1]].get("action", "related to") 
                               for i in range(len(path)-1)]
                    inferred_action = " → ".join(actions)
                    inferred.append({
                        "subject": path[0],
                        "action": inferred_action,
                        "object": path[-1],
                        "type": "inferred"
                    })
            except nx.NetworkXNoPath:
                continue
    return inferred