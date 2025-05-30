import networkx as nx
import matplotlib.pyplot as plt
import string
import os
import sys
import random

# Get current script name for filename
script_name = os.path.splitext(os.path.basename(sys.argv[0]))[0]

# Use letters A-Z for node labels
letters = list(string.ascii_uppercase)

# Create G1
G1 = nx.Graph()
# Your original graph definition
G1.add_edges_from([('A', 'B'), ('A', 'C'), ('A', 'D'), ('B', 'D'), ('B', 'E'), ('B', 'F'), ('E', 'F')])

# --- Create G2: Isomorphic to G1 but with different node labels mapping ---
# Get the original nodes from G1
original_nodes = list(G1.nodes())
# Create a list of new labels (e.g., A, B, C, D, E, F)
# We can use the same set of labels for clarity, but shuffled
new_labels = list(original_nodes) # Make a copy
random.seed(42.42) # Use a seed for reproducibility of the shuffle
random.shuffle(new_labels) # Shuffle the labels themselves

# Create a mapping from old G1 labels to the new shuffled labels
# This ensures that 'A' in G1 might map to 'D' in G2, 'B' to 'A', etc.
relabeling_map = {old_label: new_label for old_label, new_label in zip(original_nodes, new_labels)}

# Apply the relabeling to create G2. G2 will be isomorphic to G1.
G2 = nx.relabel_nodes(G1, relabeling_map)

# Verify isomorphism (optional, but good for understanding)
# print(f"Are G1 and G2 isomorphic? {nx.is_isomorphic(G1, G2)}")

# --- Plotting and Saving G1 ---
plt.figure(figsize=(6, 5)) # Create a new figure for G1
pos_g1 = nx.spring_layout(G1, seed=1) # Consistent layout for G1
nx.draw(G1, pos_g1, with_labels=True, node_color='lightblue', font_weight='bold', node_size=700)
plt.title("Graph G1 (Original)")
plt.axis('off') # Turn off the axis
# Add a label "G1" to the plot
plt.text(0.05, 0.95, 'Graph 1', transform=plt.gca().transAxes, fontsize=16,
         verticalalignment='top', bbox=dict(boxstyle='round,pad=0.3', fc='white', alpha=0.7, ec='none'))
output_file_g1 = f"{script_name}_G1.png"
plt.savefig(output_file_g1)
print(f"Saved figure as {output_file_g1}")
plt.close() # Close the figure to free memory


# --- Plotting and Saving G2 (Isomorphic, relabeled nodes) ---
plt.figure(figsize=(6, 5)) # Create a new figure for G2
pos_g2 = nx.spring_layout(G2, seed=2) # Different seed for layout of G2 to show visual difference
nx.draw(G2, pos_g2, with_labels=True, node_color='lightgreen', font_weight='bold', node_size=700)
plt.title("Graph G2 (Isomorphic with relabeled nodes)")
plt.axis('off') # Turn off the axis
# Add a label "G2" to the plot
plt.text(0.05, 0.95, 'Graph 2', transform=plt.gca().transAxes, fontsize=16,
         verticalalignment='top', bbox=dict(boxstyle='round,pad=0.3', fc='white', alpha=0.7, ec='none'))
output_file_g2 = f"{script_name}_G2.png"
plt.savefig(output_file_g2)
print(f"Saved figure as {output_file_g2}")
plt.close() # Close the figure

# --- Print neighbor counts for verification ---
print("\n--- Neighbor counts for G1 ---")
for node in sorted(G1.nodes()):
    print(f"Node {node}: {G1.degree(node)} neighbors")

print("\n--- Neighbor counts for G2 ---")
for node in sorted(G2.nodes()):
    print(f"Node {node}: {G2.degree(node)} neighbors")