import networkx as nx
import matplotlib.pyplot as plt
import string
import os
import sys
import random

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
output_file_g1 = f"{script_name}_G1.png"
plt.savefig(output_file_g1)
print(f"Saved figure as {output_file_g1}")
plt.close()

# --- Create G2 ---
original_nodes = list(G1.nodes())
new_labels = list(original_nodes)
random.seed(42.42)
random.shuffle(new_labels)
relabeling_map = {old: new for old, new in zip(original_nodes, new_labels)}
G2 = nx.relabel_nodes(G1, relabeling_map)

plt.figure(figsize=(6, 5))
pos_g2 = nx.spring_layout(G2, seed=2)
nx.draw(G2, pos_g2, with_labels=True, node_color='lightgreen', font_weight='bold', node_size=700)
plt.title("Graph G2 (Isomorphic with relabeled nodes)")
plt.axis('off')
plt.text(0.05, 0.95, 'Graph 2', transform=plt.gca().transAxes, fontsize=16,
         verticalalignment='top', bbox=dict(boxstyle='round,pad=0.3', fc='white', alpha=0.7, ec='none'))
output_file_g2 = f"{script_name}_G2.png"
plt.savefig(output_file_g2)
print(f"Saved figure as {output_file_g2}")
plt.close()

# --- Create G3 ---
G3 = nx.Graph()
G3.add_edges_from([
    ('A', 'C'), ('A', 'F'), ('B', 'F'),
    ('C', 'D'), ('C','F'), ('D', 'E'), ('E', 'F')
])

plt.figure(figsize=(6, 5))
pos_g3 = nx.spring_layout(G3, seed=4)
nx.draw(G3, pos_g3, with_labels=True, node_color='lightcoral', font_weight='bold', node_size=700)
plt.title("Graph G3")
plt.axis('off')
plt.text(0.05, 0.95, 'Graph 3', transform=plt.gca().transAxes, fontsize=16,
         verticalalignment='top', bbox=dict(boxstyle='round,pad=0.3', fc='white', alpha=0.7, ec='none'))
output_file_g3 = f"{script_name}_G3.png"
plt.savefig(output_file_g3)
print(f"Saved figure as {output_file_g3}")
plt.close()
