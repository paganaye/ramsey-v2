import networkx as nx
import matplotlib.pyplot as plt
import string
import itertools
import os
import sys

# Get current script name for filename
script_name = os.path.splitext(os.path.basename(sys.argv[0]))[0]
output_file = f"{script_name}.png"


# --- Setup ---
letters = list(string.ascii_uppercase)

# --- Graph G17 (Illustrating R(4,4) > 17 via Paley Graph P(17)) ---
# This graph shows K17 with a 2-coloring derived from the Paley Graph P(17).
# P(17) and its complement are known to be K4-free.
nodes17_count = 17
nodes17_labels = letters[:nodes17_count]  # A to Q
G17 = nx.Graph()
G17.add_nodes_from(nodes17_labels)

# Map labels (A-Q) to integers (0-16) for Paley graph construction
node_to_int_map_g17 = {label: i for i, label in enumerate(nodes17_labels)}

# Calculate quadratic residues modulo 17
# These are numbers x^2 mod 17 for x in {1, ..., (17-1)/2}
quadratic_residues_mod17 = set()
for i in range(1, (17 // 2) + 1):  # Iterate from 1 to 8
    quadratic_residues_mod17.add((i * i) % 17)
# Expected: {1, 2, 4, 8, 9, 13, 15, 16}

# Add edges to K17 and color them
# Edge (u,v) is color1 if (int(u)-int(v)) mod 17 is a quadratic residue
# Otherwise, it's color2
all_edges_k17 = list(itertools.combinations(nodes17_labels, 2))
for u_label, v_label in all_edges_k17:
    u_int = node_to_int_map_g17[u_label]
    v_int = node_to_int_map_g17[v_label]
    
    difference_mod17 = (u_int - v_int + 17) % 17 # Ensure positive difference
    
    if difference_mod17 in quadratic_residues_mod17:
        # Edge is part of P(17) - color it red
        G17.add_edge(u_label, v_label, color='red', style='solid', weight=0.5)
    else:
        # Edge is in the complement of P(17) - color it blue
        G17.add_edge(u_label, v_label, color='blue', style='dashed', weight=0.5)

# --- Graph G18 (Illustrating an instance of R(4,4) = 18) ---
# Shows K18 with a highlighted monochromatic K4 (e.g., red).
nodes18_count = 18
nodes18_labels = letters[:nodes18_count]  # A to R
G18 = nx.Graph()
G18.add_nodes_from(nodes18_labels)

all_edges_k18 = list(itertools.combinations(nodes18_labels, 2))

# Define a specific monochromatic K4 to highlight (nodes A, B, C, D form a red K4)
highlight_k4_nodes = nodes18_labels[:4]  # A, B, C, D
highlight_k4_edges_tuples = list(itertools.combinations(highlight_k4_nodes, 2))
# Convert to set of sorted tuples for efficient lookup
highlight_k4_edges_set = {tuple(sorted(edge)) for edge in highlight_k4_edges_tuples}

for u, v in all_edges_k18:
    if tuple(sorted((u, v))) in highlight_k4_edges_set:
        G18.add_edge(u, v, color='red', style='solid', weight=1.5)  # Highlighted K4
    else:
        # For this example, color all other edges blue
        G18.add_edge(u, v, color='blue', style='dashed', weight=0.3)


# --- Plotting ---
fig, axes = plt.subplots(1, 2, figsize=(20, 10)) # Adjusted figsize for larger graphs

# Plot G17
pos17 = nx.spring_layout(G17, seed=42, k=0.35, iterations=50) # Spring layout for better spread
edge_colors_g17 = [G17[u][v]['color'] for u, v in G17.edges()]
edge_styles_g17 = [G17[u][v]['style'] for u, v in G17.edges()]
edge_widths_g17 = [G17[u][v]['weight'] for u, v in G17.edges()]

nx.draw(G17, pos17, with_labels=True, ax=axes[0], node_color='skyblue', font_weight='bold',
        node_size=250, font_size=8,
        edge_color=edge_colors_g17, style=edge_styles_g17, width=edge_widths_g17, alpha=0.6)
axes[0].set_title("K17 (Paley Graph P(17) Coloring)\nNo Monochromatic K4 (R(4,4) > 17)", fontsize=12)

# Plot G18
pos18 = nx.spring_layout(G18, seed=18, k=0.35, iterations=50) # Spring layout
edge_colors_g18 = [G18[u][v]['color'] for u, v in G18.edges()]
edge_styles_g18 = [G18[u][v]['style'] for u, v in G18.edges()]
edge_widths_g18 = [G18[u][v]['weight'] for u, v in G18.edges()]

nx.draw(G18, pos18, with_labels=True, ax=axes[1], node_color='lightcoral', font_weight='bold',
        node_size=250, font_size=8,
        edge_color=edge_colors_g18, style=edge_styles_g18, width=edge_widths_g18, alpha=0.6)
axes[1].set_title(f"K18 with a Highlighted Monochromatic K4\n(e.g., Red/Solid K4 on {', '.join(highlight_k4_nodes)})", fontsize=12)

for ax in axes:
    ax.set_axis_off()

plt.suptitle("Visualizing Ramsey Number R(4,4) = 18", fontsize=16, y=0.98)
plt.tight_layout(rect=[0, 0.01, 1, 0.95]) # Adjust layout
plt.savefig(output_file, bbox_inches='tight', dpi=200) # Increased dpi
print(f"Saved figure as {output_file}")
plt.show()