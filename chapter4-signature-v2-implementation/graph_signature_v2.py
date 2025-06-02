from typing import Dict, List, Optional
from functools import total_ordering
import networkx as nx


def compare_ascending_none_last(a: Optional[int], b: Optional[int]) -> int:
    """Helper to sort lists containing None values, placing Nones last."""
    if a == b:
        return 0
    if a is None:
        return 1
    if b is None:
        return -1
    return -1 if a < b else 1


@total_ordering
class NodeSignature:
    """Represents the signature of a node in the graph at a point in time."""

    def __init__(
        self,
        neighbour_count: int,
        label: str,
        parent_node: Optional["NodeSignature"] = None,
        final_index: Optional[int] = None,
        resolution_step: Optional[int] = None,
        loop_length: Optional[int] = None,
        neighbours: Optional[List["NodeSignature"]] = None,
    ):
        self.label: Optional[str] = label
        self.neighbour_count: int = neighbour_count
        self.final_index: Optional[int] = final_index
        self.resolution_step: Optional[int] = resolution_step
        self.loop_length: Optional[int] = loop_length
        self.neighbours: Optional[List["NodeSignature"]] = neighbours
        self.parent_node: Optional["NodeSignature"] = parent_node

    def __str__(self) -> str:
        parts = []
        if self.label is not None:
            parts.append(f"Label:{self.label}")
        parts.append(f"neighbour_count:{self.neighbour_count}")
        if self.final_index is not None:
            parts.append(f"final_index:{self.final_index}")
        if self.resolution_step is not None:
            parts.append(f"resolution_step:{self.resolution_step}")
        if self.loop_length is not None:
            parts.append(f"loop_length:{self.loop_length}")

        if self.is_expanded() and self.neighbours:
            neighbour_details = []
            for n_sig in self.neighbours:
                if n_sig.is_loop():
                    neighbour_details.append(
                        f"loop(d:{n_sig.loop_length},s:{n_sig.resolution_step})"
                    )
                elif n_sig.is_finalized():
                    neighbour_details.append(
                        f"final_index(i:{n_sig.final_index},s:{n_sig.resolution_step})"
                    )
                else:
                    neighbour_details.append(
                        f"Col(nc:{n_sig.neighbour_count})")
            parts.append(f"neighbours:[{', '.join(neighbour_details)}]")

        return f"Sig({'; '.join(parts)})"

    def __repr__(self) -> str:
        return (
            f"NodeSignature(label={self.label!r}, neighbour_count={self.neighbour_count}, "
            f"final_index={self.final_index}, resolution_step={self.resolution_step}, "
            f"loop_length={self.loop_length}, "
            f"neighbours_count={len(self.neighbours) if self.neighbours is not None else 'None'})"
        )

    def is_collapsed(self) -> bool:
        return self.neighbours is None

    def is_expanded(self) -> bool:
        return self.neighbours is not None

    def is_loop(self) -> bool:
        return self.loop_length is not None

    def is_finalized(self) -> bool:
        return self.final_index is not None

    def is_resolved(self) -> bool:
        return self.resolution_step is not None

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, NodeSignature):
            return NotImplemented
        return compare_signatures(self, other) == 0

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, NodeSignature):
            return NotImplemented
        return compare_signatures(self, other) < 0


def compare_signatures(sig_a: NodeSignature, sig_b: NodeSignature) -> int:
    """Compares two signatures based on a set of hierarchical rules."""
    diff_nc = sig_b.neighbour_count - sig_a.neighbour_count
    if diff_nc != 0:  # 1. By neighbour_count (descending)
        return diff_nc

    fs_cmp = compare_ascending_none_last(
        sig_a.resolution_step, sig_b.resolution_step)
    if fs_cmp != 0:  # 2. resolution_step step
        return fs_cmp

    cd_cmp = compare_ascending_none_last(sig_a.loop_length, sig_b.loop_length)
    if cd_cmp != 0:  # 3. loop_length
        return cd_cmp

    fi_cmp = compare_ascending_none_last(sig_a.final_index, sig_b.final_index)
    if fi_cmp != 0:  # 4. final_index
        return fi_cmp

    has_n_a = sig_a.neighbours is not None
    has_n_b = sig_b.neighbours is not None
    if has_n_a != has_n_b:
        # The signature with neighbours (EXPANDED) comes first
        return -1 if has_n_a else 1

    if has_n_a and has_n_b:
        for i in range(sig_a.neighbour_count):
            comparison_result = compare_signatures(
                sig_a.neighbours[i], sig_b.neighbours[i]
            )
            if comparison_result != 0:
                return comparison_result

    # signatures are considered equal or ambiguous for now.
    return 0


class GraphSignatures:
    """Manages the computation of canonical signatures for a graph."""

    def __init__(self, graph: nx.Graph):
        self.graph: nx.Graph = graph
        self.signatures_map: Dict[str, NodeSignature] = {}
        for node_label_nx in self.graph.nodes():
            label_str = str(node_label_nx)
            self.signatures_map[label_str] = NodeSignature(
                label=label_str,
                neighbour_count=self.graph.degree(node_label_nx),
            )
        self.all_signatures: List[NodeSignature] = list(
            self.signatures_map.values())

    def expand_signature_node(self, sig_to_expand: NodeSignature, pass_number: int) -> bool:
        if sig_to_expand.is_finalized() or sig_to_expand.is_expanded() or sig_to_expand.is_loop():
            return False

        new_neighbours: List[NodeSignature] = []
        current_node_label = str(sig_to_expand.label)

        for neighbour_label_nx in self.graph.neighbors(current_node_label):
            neighbour_label = str(neighbour_label_nx)
            loop_len: Optional[int] = None
            parent_iterator = sig_to_expand
            distance_counter = 1
            while parent_iterator is not None:
                if str(parent_iterator.label) == neighbour_label:
                    loop_len = distance_counter
                    break
                parent_iterator = parent_iterator.parent_node
                distance_counter += 1

            if loop_len is not None:
                new_neighbour = NodeSignature(
                    label=neighbour_label,
                    neighbour_count=self.signatures_map[neighbour_label].neighbour_count,
                    loop_length=loop_len,
                    resolution_step=pass_number,
                    parent_node=sig_to_expand,
                )
            else:
                neighbour_sig_obj = self.signatures_map[neighbour_label]
                if neighbour_sig_obj.is_finalized():
                    new_neighbour = NodeSignature(
                        label=neighbour_label,
                        neighbour_count=neighbour_sig_obj.neighbour_count,
                        final_index=neighbour_sig_obj.final_index,
                        resolution_step=neighbour_sig_obj.resolution_step,
                        parent_node=sig_to_expand,
                    )
                else:
                    new_neighbour = NodeSignature(
                        label=neighbour_label,
                        neighbour_count=neighbour_sig_obj.neighbour_count,
                        parent_node=sig_to_expand,
                    )
            new_neighbours.append(new_neighbour)

        new_neighbours.sort()
        sig_to_expand.neighbours = new_neighbours
        return True

    def process_pass(self, pass_number: int) -> bool:
        self.all_signatures.sort()
        made_progress = False
        for i, sig in enumerate(self.all_signatures):
            if sig.is_finalized():
                continue

            is_unique_from_prev = (i == 0) or (
                compare_signatures(sig, self.all_signatures[i - 1]) != 0)
            is_unique_from_next = (i == len(self.all_signatures) - 1) or (
                compare_signatures(sig, self.all_signatures[i + 1]) != 0)

            if is_unique_from_prev and is_unique_from_next:
                sig.final_index = i
                sig.resolution_step = pass_number
                made_progress = True
        return made_progress

    def all_are_finalized(self) -> bool:
        return all(s.is_finalized() for s in self.all_signatures)

    def expand_ambiguous_nodes(self, pass_number: int) -> bool:
        any_expansion_occurred = False
        for sig_obj in list(self.all_signatures):
            if not sig_obj.is_finalized():
                if self.expand_node(sig_obj, pass_number):
                    any_expansion_occurred = True

        if any_expansion_occurred:
            self.all_signatures.sort()
        return any_expansion_occurred

    def expand_node(self, sig_obj: "NodeSignature", pass_number: int) -> bool:
        if sig_obj.is_loop() or sig_obj.is_finalized():
            return False

        any_expansion_occurred = False
        if sig_obj.is_expanded():
            for neighbor_sig in sig_obj.neighbours:
                if self.expand_node(neighbor_sig, pass_number):
                    any_expansion_occurred = True
        else:
            self.expand_signature_node(sig_obj, pass_number)
            any_expansion_occurred = True

        if any_expansion_occurred and sig_obj.neighbours is not None:
            sig_obj.neighbours.sort()
        return any_expansion_occurred

    def compute_all_signatures(self):
        pass_number = 1
        max_passes = len(self.graph.nodes()) + 2
        while pass_number <= max_passes:
            made_progress = self.process_pass(pass_number)
            if self.all_are_finalized():
                break
            if not made_progress and pass_number > 1:
                if not self.expand_ambiguous_nodes(pass_number):
                    break
            pass_number += 1

        if not self.all_are_finalized():
            raise Exception(
                f"Algorithm did not converge after {max_passes} passes. "
                f"Graph: {list(self.graph.nodes())}, Edges: {list(self.graph.edges())}. "
                f"Not all node signatures were finalized."
            )
