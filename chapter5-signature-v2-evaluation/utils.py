import colorsys
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import networkx as nx
from graph_signature_v2 import GraphSignatures
import networkx as nx
from typing import Union, Tuple
import string

# =============================================================================================================================
# ============  helper functions for this notebook                                                                 ============
# =============================================================================================================================

def hsl_color(level: int, max_level: int = 4) -> str:
    """Generates a shade of green based on the finalization level."""
    hue = 120 / 360
    saturation = 1.0
    lightness = 0.3 + (level - 1) * (0.5 / max(1, max_level - 1)) if max_level > 1 else 0.5
    rgb = colorsys.hls_to_rgb(hue, lightness, saturation)
    return mcolors.to_hex(rgb)


# --- Visualization ---

_FIXED_POS = {}

STATUS_COLORS = {
    "done": "lightgreen",
    "pending": "orange",
    "error": "red",
    "default": "lightgray",
}

def make_figure(signatures: GraphSignatures, title: str):
    """Draws the graph with nodes colored by their finalization level."""
    global _FIXED_POS
    graph = signatures.graph

    if not _FIXED_POS:
        _FIXED_POS = nx.spring_layout(graph, seed=42)

    node_colors = []
    signature_map = signatures.signatures_map
    max_level = max(
        (sig.resolution_step for sig in signature_map.values() if sig.is_finalized() and sig.resolution_step is not None),
        default=1,
    )

    for node in graph.nodes():
        color = "lightgray"
        node_label = str(node)
        if node_label in signature_map:
            signature = signature_map[node_label]
            if signature.is_finalized() and signature.resolution_step is not None:
                color = hsl_color(signature.resolution_step, max_level=max_level)
        node_colors.append(color)

    plt.figure(figsize=(10, 6))
    nx.draw(
        graph,
        pos=_FIXED_POS,
        with_labels=True,
        node_color=node_colors,
        edge_color="gray",
        arrows=False,
    )
    plt.title(title)
    plt.show()

def get_signature(graph_input: Union[nx.Graph, str]) -> GraphSignatures:
    if isinstance(graph_input, nx.Graph):
        graph = graph_input
    elif isinstance(graph_input, str):
        graph = nx.from_graph6_bytes(graph_input.encode('ascii'))
    else:
        raise TypeError("Input must be a nx.Graph object or a g6 string.")

    if graph.order() > len(string.ascii_uppercase):
        raise ValueError("Cannot relabel graph with > 26 nodes to single letters.")
    
    mapping = {i: string.ascii_uppercase[i] for i in range(graph.order())}
    graph = nx.relabel_nodes(graph, mapping)
    
    gs = GraphSignatures(graph)
    gs.compute_all_signatures()
    
    return gs 

def check(message, condition: bool):
    if condition:
        print(f"✅ {message}")
    else:
        print(f"❌ {message}")    