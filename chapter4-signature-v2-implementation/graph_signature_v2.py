import colorsys
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
# Tuple est utilisé par process_pass
from typing import Dict, List, Optional, Tuple
from functools import total_ordering

import networkx as nx


def compare_ascending_none_last(a: Optional[int], b: Optional[int]) -> int:
    return (
        0
        if a == b
        else (1 if a is None else (-1 if b is None else (-1 if a < b else 1)))
    )


@total_ordering
class NodeSignature:
    def __init__(
        self,
        neighbourCount: int,
        label: str,
        path: List[str] = [],
        finalIndex: Optional[int] = None,
        resolutionStep: Optional[int] = None,
        cycleDistance: Optional[int] = None,
        neighbours: Optional[List["NodeSignature"]] = None,
    ):
        self.label: Optional[str] = label
        self.neighbourCount: int = neighbourCount
        self.finalIndex: Optional[int] = finalIndex
        self.resolutionStep: Optional[int] = resolutionStep
        self.cycleDistance: Optional[int] = cycleDistance
        self.neighbours: Optional[List["NodeSignature"]] = neighbours

    def __str__(self) -> str:
        parts = []
        if self.label is not None:
            parts.append(f"Label:{self.label}")
        parts.append(f"neighbourCount:{self.neighbourCount}")
        if self.finalIndex is not None:
            parts.append(f"finalIndex:{self.finalIndex}")
        if self.resolutionStep is not None:
            parts.append(f"resolutionStep:{self.resolutionStep}")
        if self.cycleDistance is not None:
            parts.append(f"cycleDistance:{self.cycleDistance}")

        if self.isExpanded() and self.neighbours:
            neighbour_details = []
            for n_sig in self.neighbours:
                if n_sig.isLoop():
                    neighbour_details.append(
                        f"loop(d:{n_sig.cycleDistance},s:{n_sig.resolutionStep})"
                    )
                elif n_sig.isFinalized():
                    neighbour_details.append(
                        f"finalIndex(i:{n_sig.finalIndex},s:{n_sig.resolutionStep})"
                    )
                else:  # Collapsed representation within neighbours
                    neighbour_details.append(f"Col(nc:{n_sig.neighbourCount})")
            parts.append(f"neighbours:[{', '.join(neighbour_details)}]")

        return f"Sig({'; '.join(parts)})"

    def __repr__(self) -> str:
        return (
            f"NodeSignature(label = {self.label!r}, neighbourCount = {self.neighbourCount}, "
            f"finalIndex = {self.finalIndex}, resolutionStep = {self.resolutionStep}, "
            f"cycleDistance = {self.cycleDistance}, "
            f"neighboursCount = {len(self.neighbours) if self.neighbours is not None else 'None'})"
        )

    def isCollapsed(self) -> bool:
        return self.neighbours is None

    def isExpanded(self) -> bool:
        return self.neighbours is not None

    def isLoop(self) -> bool:
        return self.cycleDistance is not None

    def isFinalized(self) -> bool:
        return self.finalIndex is not None

    def isResolved(self) -> bool:
        return self.resolutionStep is not None

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, NodeSignature):
            return NotImplemented
        return compare_signatures(self, other) == 0

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, NodeSignature):
            return NotImplemented
        return compare_signatures(self, other) < 0


def compare_signatures(sig_a: NodeSignature, sig_b: NodeSignature) -> int:

    diff_nc = sig_b.neighbourCount - sig_a.neighbourCount
    if diff_nc != 0:  # 1. By neighbourCount (descending)
        return diff_nc

    fs_cmp = compare_ascending_none_last(
        sig_a.resolutionStep, sig_b.resolutionStep)
    if fs_cmp != 0:  # 4. ResolutionStep step
        return fs_cmp

    cd_cmp = compare_ascending_none_last(
        sig_a.cycleDistance, sig_b.cycleDistance)
    if cd_cmp != 0:  # 3. Cycle distance
        return cd_cmp

    fi_cmp = compare_ascending_none_last(sig_a.finalIndex, sig_b.finalIndex)
    if fi_cmp != 0:  # 2. Final index
        return fi_cmp

    has_n_a = sig_a.neighbours is not None
    has_n_b = sig_b.neighbours is not None

    if has_n_a != has_n_b:
        # The one with neighbours (EXPANDED) comes first
        return -1 if has_n_a else 1

    if has_n_a and has_n_b:  # 5. Neighbours
        for i in range(sig_a.neighbourCount):
            comparison_result = compare_signatures(
                sig_a.neighbours[i], sig_b.neighbours[i]
            )
            if comparison_result != 0:
                return comparison_result

    # signatures are considered equal for now.
    return 0


class GraphSignatures:
    def __init__(self, graph: nx.Graph):
        self.graph: nx.Graph = graph
        self.signatures_map: Dict[str, NodeSignature] = {}
        for node_label_nx in self.graph.nodes():
            label_str = str(node_label_nx)
            self.signatures_map[label_str] = NodeSignature(
                label=label_str,
                neighbourCount=self.graph.degree(node_label_nx),
                path=[],
            )

        self.all_signatures: List[NodeSignature] = list(
            self.signatures_map.values())

    def expand_signature_node(
        self,
        signature_to_expand: NodeSignature,
        pass_number: int,
        expansion_path: List[str],
    ) -> bool:
        if (
            signature_to_expand.isFinalized()
            or signature_to_expand.isExpanded()
            or signature_to_expand.isLoop()
        ):
            return False

        new_neighbours: List[NodeSignature] = []
        current_node_label_str = str(signature_to_expand.label)

        for neighbour_node_label_nx in self.graph.neighbors(current_node_label_str):
            neighbour_label = str(neighbour_node_label_nx)

            new_neighbour: NodeSignature
            if neighbour_label in expansion_path:
                cycle_dist = len(expansion_path) - \
                    expansion_path.index(neighbour_label)

                new_neighbour = NodeSignature(
                    label=neighbour_label,
                    neighbourCount=self.signatures_map[neighbour_label].neighbourCount,
                    cycleDistance=cycle_dist,
                    resolutionStep=pass_number,
                    path=[],  # ...TODO own path + neighbour_label
                )
            else:
                neighbour_sig_obj = self.signatures_map[neighbour_label]
                if neighbour_sig_obj.isFinalized():
                    new_neighbour = NodeSignature(
                        label=neighbour_label,
                        neighbourCount=neighbour_sig_obj.neighbourCount,
                        finalIndex=neighbour_sig_obj.finalIndex,
                        resolutionStep=neighbour_sig_obj.resolutionStep,
                        path=[],  # ...TODO own path + neighbour_label
                    )
                else:
                    new_neighbour = NodeSignature(
                        label=neighbour_label,
                        neighbourCount=neighbour_sig_obj.neighbourCount,
                        path=[],  # ...TODO own path + neighbour_label
                    )
            new_neighbours.append(new_neighbour)

        new_neighbours.sort()

        signature_to_expand.neighbours = new_neighbours
        return True

    def process_pass(self, pass_number: int) -> bool:
        self.all_signatures.sort()

        made_progress = False
        for i, sig in enumerate(self.all_signatures):
            if sig.isFinalized():  # Skip if already finalized
                continue

            is_unique_from_prev = (i == 0) or (
                compare_signatures(sig, self.all_signatures[i - 1]) != 0
            )
            is_unique_from_next = (i == len(self.all_signatures) - 1) or (
                compare_signatures(sig, self.all_signatures[i + 1]) != 0
            )

            if is_unique_from_prev and is_unique_from_next:
                sig.finalIndex = i  # The new global index after sorting
                sig.resolutionStep = pass_number
                made_progress = True

        return made_progress

    def all_finalized(self) -> bool:
        return all(s.isFinalized() for s in self.all_signatures)

    def expand_ambiguous_nodes(self, pass_number: int) -> bool:
        any_expansion_occurred = False
        for sig_obj in list(self.all_signatures):
            if not sig_obj.isFinalized():
                initial_path = [str(sig_obj.label)]
                if self.expand_node(sig_obj, pass_number, initial_path):
                    any_expansion_occurred = True

        if any_expansion_occurred:
            self.all_signatures.sort()

        return any_expansion_occurred

    def expand_node(
        self, sig_obj: "NodeSignature", pass_number: int, path: List[str]
    ) -> bool:
        if sig_obj.isLoop() or sig_obj.isFinalized():
            return False

        any_expansion_occurred = False

        if sig_obj.neighbours:
            for neighbor_sig in sig_obj.neighbours:
                new_path = path + [str(neighbor_sig.label)]
                if self.expand_node(neighbor_sig, pass_number, new_path):
                    any_expansion_occurred = True
        else:
            self.expand_signature_node(sig_obj, pass_number, path)
            any_expansion_occurred = True

        if any_expansion_occurred:
            sig_obj.neighbours.sort()
        return any_expansion_occurred

    def compute_all_signatures(self):
        pass_number = 1
        max_passes = len(self.graph.nodes()) + 2

        while pass_number <= max_passes:
            made_progress_in_finalization = self.process_pass(pass_number)

            if self.all_finalized():
                break

            if not made_progress_in_finalization and pass_number > 1:
                break

            self.expand_ambiguous_nodes(pass_number)

            pass_number += 1


# =============================================================================================================================
# ============  helper functions for this notebook                                                                 ============
# =============================================================================================================================


def hsl_color(level: int, max_level: int = 4):
    """Generates a shade of green based on the finalization level."""
    hue = 120 / 360  # Green
    saturation = 1.0
    # Lightness varies from dark (0.3) to light (0.8)
    lightness = 0.3 + (level - 1) * (0.5 / max(1, max_level - 1))
    rgb = colorsys.hls_to_rgb(hue, lightness, saturation)
    return mcolors.to_hex(rgb)


_fixed_pos = {}

STATUS_COLORS = {
    "done": "lightgreen",
    "pending": "orange",
    "error": "red",
    "default": "lightgray",
}


def make_fig(sigs: GraphSignatures, title: str):
    """
    Visualization function adapted to work with the GraphSignatures class
    without requiring a get_finalization_level method.
    """
    global _fixed_pos
    G = sigs.graph

    # Use a fixed layout for consistent visualization across steps
    if not _fixed_pos:
        _fixed_pos = nx.spring_layout(G, seed=42)

    node_colors = []
    # Directly access the signature map from the sigs object
    signature_map = sigs.signatures_map

    # Determine the maximum finalization level for better color scaling
    max_finalized_level = max(
        (
            sig.resolutionStep
            for sig in signature_map.values()
            if sig.isFinalized() and sig.resolutionStep is not None
        ),
        default=1,
    )

    for node in G.nodes():
        color = "lightgray"  # Default color for non-finalized nodes
        node_label_str = str(node)

        # Check if the signature exists and is finalized
        if node_label_str in signature_map:
            signature = signature_map[node_label_str]
            if signature.isFinalized() and signature.resolutionStep is not None:
                # Use the resolutionStep to determine the color
                level = signature.resolutionStep
                color = hsl_color(level, max_level=max_finalized_level)

        node_colors.append(color)

    plt.figure(figsize=(10, 6))
    # Assuming the graph is undirected, so arrows are set to False
    nx.draw(
        G,
        pos=_fixed_pos,
        with_labels=True,
        node_color=node_colors,
        edge_color="gray",
        arrows=False,
    )
    plt.title(title)
    plt.show()
