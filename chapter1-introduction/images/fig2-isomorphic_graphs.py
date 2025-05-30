import networkx as nx
import matplotlib.pyplot as plt
import string
import os
import sys

# Get current script name for filename
script_name = os.path.splitext(os.path.basename(sys.argv[0]))[0]
output_file = f"{script_name}.png"

# Use letters A-Z for node labels
letters = list(string.ascii_uppercase)

# Create G1: a 4-node graph (triangle + tail)
G1 = nx.Graph()
G1.add_edges_from([(0, 1), (1, 2), (2, 3), (0, 2)])
G1 = nx.relabel_nodes(G1, lambda x: letters[x])

# Create isomorphic G2 by permuting nodes
mapping = {letter: letters[i] for i, letter in enumerate(['C', 'A', 'B', 'D'])}
G2 = nx.relabel_nodes(G1, mapping)

# Plot
fig, axes = plt.subplots(1, 2, figsize=(10, 4))

pos = nx.spring_layout(G1, seed=1)  # Same layout for both
nx.draw(G1, pos, with_labels=True, ax=axes[0], node_color='lightblue', font_weight='bold')
axes[0].set_title("Graph G1 (canonical labeling)")

nx.draw(G2, pos, with_labels=True, ax=axes[1], node_color='lightgreen', font_weight='bold')
axes[1].set_title("Graph G2 (isomorphic variant)")

for ax in axes:
    ax.set_axis_off()

plt.tight_layout()
plt.savefig(output_file)
print(f"Saved figure as {output_file}")
plt.show()
