import os
import sys
from graphviz import Digraph # type: ignore

script_name = os.path.splitext(os.path.basename(sys.argv[0]))[0]

dot = Digraph(comment="Algorithm Process Flowchart")
# J'utilise votre dernier size="10,5", rankdir="TB"
dot.attr(rankdir="TB", size="10,5", label="Signature v2 Main Flow", fontsize="16")
dot.attr("node", fontname="Helvetica")  # Police par défaut pour les noeuds
dot.attr(
    "edge", fontname="Helvetica", fontsize="10"
)  # Police et taille pour les labels d'arêtes

# Définition des nœuds principaux du processus
dot.node("I", "Init", shape="ellipse", style="filled", fillcolor="lightblue")
dot.node("S", "Sort Signatures", shape="box", style="filled", fillcolor="lightyellow")
dot.node(
    "E",
    "Expand recursively all\nambiguous signatures",
    shape="box",
    style="filled",
    fillcolor="lightyellow",
)

# Définition des nœuds terminaux (les "ronds verts")
# Ils seront groupés pour être placés en bas
dot.node(
    "C",
    "algorithm complete",
    shape="ellipse",
    style="filled",
    color="darkgreen",
    fillcolor="#A1ECA1",
    fontcolor="darkgreen",
)

# Définition du flux de l'algorithme
dot.edge("I", "S")
dot.edge("S", "C", label=" all signatures\n are unique")
dot.edge("S", "E", label=" ambiguous\nsignatures\n remain")
dot.edge("E", "AMB", label="expansion\nsuccess")  # Label clarifié
dot.edge("AMB", "S", label=" next pass")

dot.node(
    "AMB",
    "Pass complete\nAmbiguous nodes remain",
    shape="ellipse",
    style="filled",
    fillcolor="lightgoldenrodyellow",
)

dot.edge("E", "C", label="No expansion\n(Symmetry detected)")  # Label clarifié

# Grouper les nœuds terminaux C et SYM pour les forcer en bas
with dot.subgraph() as s:
    s.attr(rank="sink")  # Attribut clé pour le positionnement en bas
    s.node("C")

# Rendu du graphe
output_file = f"{script_name}"
dot.render(output_file, view=False, cleanup=True, format="png")

print(f"Saved flowchart diagram as {output_file}.png")
