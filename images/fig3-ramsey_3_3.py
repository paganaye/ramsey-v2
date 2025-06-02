import networkx as nx
import matplotlib.pyplot as plt
import string
import itertools
import os
import sys

# --- Setup ---
letters = list(string.ascii_uppercase)
script_name = os.path.splitext(os.path.basename(sys.argv[0]))[0]
output_file = f"{script_name}.png"

# --- Graph G5 (Illustrating R(3,3) > 5) ---
# This graph shows a K5 with a 2-coloring that has no monochromatic K3.
# Nodes are A, B, C, D, E.
# Color1 (e.g., red, solid line) for the 5-cycle.
# Color2 (e.g., blue, dashed line) for the inner pentagram.

nodes5_labels = letters[:5]  # A, B, C, D, E
G5 = nx.Graph()
G5.add_nodes_from(nodes5_labels)

# Define edges for Color1 (red 5-cycle)
edges_color1_g5 = []
for i in range(5):
    u, v = nodes5_labels[i], nodes5_labels[(i + 1) % 5]
    G5.add_edge(u, v, color='red', style='solid', weight=2.0)
    edges_color1_g5.append(tuple(sorted((u, v)))) # Store for lookup

# Define edges for Color2 (blue pentagram)
all_edges_k5 = list(itertools.combinations(nodes5_labels, 2))
for u, v in all_edges_k5:
    if tuple(sorted((u, v))) not in edges_color1_g5:
        G5.add_edge(u, v, color='blue', style='dashed', weight=2.0)

# --- Graph G6 (Illustrating R(3,3) = 6) ---
# This graph shows a K6 with an example 2-coloring,
# highlighting one resulting monochromatic K3 (e.g., a red K3).
# Nodes are A, B, C, D, E, F.

nodes6_labels = letters[:6]  # A, B, C, D, E, F
G6 = nx.Graph()
G6.add_nodes_from(nodes6_labels)

all_edges_k6 = list(itertools.combinations(nodes6_labels, 2))

# Define a specific monochromatic K3 to highlight (e.g., nodes A, B, C form a red K3)
highlight_k3_nodes = [nodes6_labels[0], nodes6_labels[1], nodes6_labels[2]]  # A, B, C
highlight_k3_edges = list(itertools.combinations(highlight_k3_nodes, 2))
highlight_k3_edges_sorted = [tuple(sorted(edge)) for edge in highlight_k3_edges]

for u, v in all_edges_k6:
    if tuple(sorted((u, v))) in highlight_k3_edges_sorted:
        G6.add_edge(u, v, color='red', style='solid', weight=3.0)  # Highlighted K3
    else:
        # For this example, color all other edges blue
        G6.add_edge(u, v, color='blue', style='dashed', weight=1.0)


# --- Plotting ---
fig, axes = plt.subplots(1, 2, figsize=(14, 7)) # Increased figsize for clarity

# Plot G5
pos5 = nx.circular_layout(G5) # Circular layout is standard for this K5 example
edge_colors_g5 = [G5[u][v]['color'] for u, v in G5.edges()]
edge_styles_g5 = [G5[u][v]['style'] for u, v in G5.edges()]
edge_widths_g5 = [G5[u][v]['weight'] for u, v in G5.edges()]

nx.draw(G5, pos5, with_labels=True, ax=axes[0], node_color='skyblue', font_weight='bold',
        node_size=700, font_size=10,
        edge_color=edge_colors_g5, style=edge_styles_g5, width=edge_widths_g5)
axes[0].set_title("K5 with no monochromatic K3 (R(3,3) > 5)\nRed/Solid = Cycle, Blue/Dashed = Pentagram", fontsize=12)

# Plot G6
pos6 = nx.circular_layout(G6) # Circular layout for K6
edge_colors_g6 = [G6[u][v]['color'] for u, v in G6.edges()]
edge_styles_g6 = [G6[u][v]['style'] for u, v in G6.edges()]
edge_widths_g6 = [G6[u][v]['weight'] for u, v in G6.edges()]

nx.draw(G6, pos6, with_labels=True, ax=axes[1], node_color='lightcoral', font_weight='bold',
        node_size=700, font_size=10,
        edge_color=edge_colors_g6, style=edge_styles_g6, width=edge_widths_g6)
axes[1].set_title(f"K6 with a highlighted Monochromatic K3\n(e.g., Red/Solid K3 on {', '.join(highlight_k3_nodes)})", fontsize=12)

for ax in axes:
    ax.set_axis_off()

plt.suptitle("Visualizing Ramsey Number R(3,3) = 6", fontsize=16, y=0.98)
plt.tight_layout(rect=[0, 0.02, 1, 0.95]) # Adjust for suptitle and bottom margin
plt.savefig(output_file, bbox_inches='tight')
print(f"Saved figure as {output_file}")
plt.show()