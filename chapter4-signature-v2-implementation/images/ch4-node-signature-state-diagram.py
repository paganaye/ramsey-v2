import os
import sys
from graphviz import Digraph

script_name = os.path.splitext(os.path.basename(sys.argv[0]))[0]

# --- Diagramme simplifié du cycle de vie d'un objet Signature ---

dot = Digraph(comment="Signature Object Lifecycle")
# Style cohérent avec le premier graphe
dot.attr(rankdir="TB", size="10,8", label="Lifecycle of a Single Signature Object", fontsize="16")
dot.attr('node', fontname="Helvetica", style="filled")
dot.attr('edge', fontname="Helvetica", fontsize="10")

# Définition des états possibles pour une signature
# Modifié pour utiliser 'ellipse' pour les états non terminaux pour la clarté
dot.node("COLLAPSED", "Collapsed", shape="ellipse", fillcolor="lightblue")
dot.node("EXPANDED", "Expanded", shape="ellipse", fillcolor="lightyellow")

# Définition des états terminaux
dot.node("FINALIZED", "Unique", shape="doublecircle", color="darkgreen", fillcolor="#A1ECA1", fontcolor="darkgreen", fixedsize="true", width="1.5", height="1.5")
dot.node("STABLE", "Symmetric", shape="doublecircle", color="darkorange", fillcolor="#FFDAB9", fontcolor="darkorange", fixedsize="true", width="1.5", height="1.5")

# Définition des transitions logiques
# Depuis l'état Collapsed
dot.edge("COLLAPSED", "FINALIZED", label="unique")
dot.edge("COLLAPSED", "EXPANDED", label="ambiguous")

# Depuis l'état Expanded
dot.edge("EXPANDED", "FINALIZED", label="unique")
dot.edge("EXPANDED", "STABLE", label=" algorithm\n terminates")
dot.edge("EXPANDED", "EXPANDED", label=" next pass")

# Forcer les états terminaux à être en bas
with dot.subgraph() as s:
    s.attr(rank='sink')
    s.node("FINALIZED")
    s.node("STABLE")

# Rendu du graphe
output_file = f"{script_name}" # Nom de fichier selon votre dernière version
dot.render(output_file, view=False, cleanup=True, format="png")

print(f"Saved signature lifecycle diagram as {output_file}.png")
