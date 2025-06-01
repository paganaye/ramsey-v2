import networkx as nx
import matplotlib.pyplot as plt
import string
import os
import sys
import random
import os
import sys
from graphviz import Digraph

script_name = os.path.splitext(os.path.basename(sys.argv[0]))[0]
letters = list(string.ascii_uppercase)

# --- Create G1 ---
G1 = nx.Graph()
G1.add_edges_from([
    ('A', 'B'), ('A', 'C'), ('A', 'D'),
    ('B', 'D'), ('B', 'E'), ('B', 'F'),
    ('E', 'F')
])

plt.figure(figsize=(6, 5))
pos_g1 = nx.spring_layout(G1, seed=1)
nx.draw(G1, pos_g1, with_labels=True, node_color='lightblue', font_weight='bold', node_size=700)
plt.title("Graph G1 (Original)")
plt.axis('off')
plt.text(0.05, 0.95, 'Graph 1', transform=plt.gca().transAxes, fontsize=16,
         verticalalignment='top', bbox=dict(boxstyle='round,pad=0.3', fc='white', alpha=0.7, ec='none'))
output_file_g1 = f"{script_name}.png"
plt.savefig(output_file_g1)
print(f"Saved figure as {output_file_g1}")
plt.close()

