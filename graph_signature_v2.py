import string
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


class Node:
    def __init__(
        self,
        label: str,
        neighbour_count: int,
        final_index: Optional[int] = None,
        resolution_step: Optional[int] = None
    ):
        self.label: str = label
        self.neighbour_count: int = neighbour_count
        self.final_index: Optional[int] = final_index
        self.resolution_step: Optional[int] = resolution_step
        self.neighbours: List["Node"] = []

    @property
    def is_finalized(self) -> bool:
        return self.final_index is not None

    @property
    def is_resolved(self) -> bool:
        return self.resolution_step is not None

@total_ordering
class NodeSignature:
    """Represents the signature of a node in the graph at a point in time."""

    def __init__(
        self,
        node: Node,
        parent_sig: Optional["NodeSignature"] = None,
        neighbours: Optional[List["NodeSignature"]] = None,
        loop_length: Optional[int] = None,
    ):
        self.node = node
        self.loop_length: Optional[int] = loop_length
        self.neighbours: Optional[List["NodeSignature"]] = neighbours
        self.parent_sig: Optional["NodeSignature"] = parent_sig

    def __str__(self) -> str:
        parts = []
        if self.label is not None:
            parts.append(f"label:{self.label}")
        parts.append(f"neighbour_count:{self.neighbour_count}")
        if self.final_index is not None:
            parts.append(f"final_index:{self.final_index}")
        if self.resolution_step is not None:
            parts.append(f"resolution_step:{self.resolution_step}")
        if self.loop_length is not None:
            parts.append(f"loop_length:{self.loop_length}")

        if self.is_expanded and self.neighbours:
            neighbour_details = [str(n_sig) for n_sig in self.neighbours]
            parts.append(f"neighbours:[{', '.join(neighbour_details)}]")

        return "{" + ','.join(parts)+"}"

    def sig(self) -> str:
        parts = []
        parts.append(f"nc:{self.neighbour_count}")
        if self.final_index is not None:
            parts.append(f"fi:{self.final_index}")
        if self.resolution_step is not None:
            parts.append(f"rs:{self.resolution_step}")
        if self.loop_length is not None:
            parts.append(f"ll:{self.loop_length}")
        if self.is_expanded and self.neighbours:
            neighbour_details = [n_sig.sig() for n_sig in self.neighbours]
            parts.append(f"n:[{','.join(neighbour_details)}]")
        return "{" + ','.join(parts) + "}"

    @property
    def neighbour_count(self) -> bool:
        return self.node.neighbour_count

    @property
    def final_index(self) -> int:
        return self.node.final_index

    @property
    def resolution_step(self) -> int:
        return self.node.resolution_step

    @property
    def label(self) -> string:
        return self.node.label

    @property
    def is_finalized(self) -> bool:
        return self.node.is_finalized

    @property
    def is_resolved(self) -> bool:
        return self.node.is_resolved

    @property
    def is_collapsed(self) -> bool:
        return self.neighbours is None

    @property
    def is_expanded(self) -> bool:
        return self.neighbours is not None

    @property
    def is_loop(self) -> bool:
        return self.loop_length is not None

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
        # The length of neighbours should be the same if neighbour_count is the same
        for i in range(len(sig_a.neighbours)):
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
        self.nodes_map: Dict[str, Node] = {}

        for node_label_nx in self.graph.nodes():
            label_str = str(node_label_nx)
            self.nodes_map[label_str] = Node(
                label=label_str,
                neighbour_count=self.graph.degree(node_label_nx)
            )

        for node_obj in self.nodes_map.values():
            for neighbour_label_nx in self.graph.neighbors(node_obj.label):
                neighbour_node_obj = self.nodes_map[str(neighbour_label_nx)]
                node_obj.neighbours.append(neighbour_node_obj)
        
        self.signatures_map: Dict[str, NodeSignature] = {
            label: NodeSignature(node=node_obj)
            for label, node_obj in self.nodes_map.items()
        }
        self.all_signatures: List[NodeSignature] = list(
            self.signatures_map.values())

    def expand_signature_node(self, sig_to_expand: NodeSignature, pass_number: int) -> bool:
        if sig_to_expand.is_finalized or sig_to_expand.is_expanded or sig_to_expand.is_loop:
            return False

        new_neighbours_sigs: List[NodeSignature] = []
        
        for neighbour_node in sig_to_expand.node.neighbours:
            neighbour_label = neighbour_node.label
            loop_len: Optional[int] = None

            parent_iterator = sig_to_expand
            distance_counter = 1
            while parent_iterator is not None:
                if parent_iterator.node.label == neighbour_label: 
                    loop_len = distance_counter
                    break
                parent_iterator = parent_iterator.parent_sig
                distance_counter += 1
            
            new_neighbour_sig = NodeSignature(
                node=neighbour_node, 
                loop_length=loop_len,
                parent_sig=sig_to_expand,
            )
            new_neighbours_sigs.append(new_neighbour_sig)

        new_neighbours_sigs.sort()
        sig_to_expand.neighbours = new_neighbours_sigs 
        return True

    def process_pass(self, pass_number: int) -> bool:
        self.all_signatures.sort()
        made_progress = False
        for i, sig in enumerate(self.all_signatures):
            if sig.is_finalized:
                # if sig.final_index != i:
                #     error_message_parts = [
                #         f"Internal Error: Finalized signature's index changed during pass {pass_number}.",
                #         f"  Problematic Signature Details:",
                #         f"    - Full Signature: {str(sig)}",
                #         f"    - Label: {sig.label}",
                #         f"    - Originally assigned final_index: {sig.final_index}",
                #         f"    - Original resolution_step: {sig.resolution_step}",
                #         f"    - Current index in sorted list: {i}",
                #     ]

                #     # Check what's at the original final_index now, if valid
                #     if 0 <= sig.final_index < len(self.all_signatures):
                #         sig_at_original_pos = self.all_signatures[sig.final_index]
                #         error_message_parts.append(
                #             f"  Signature currently at index {sig.final_index} (original position of problematic sig): {str(sig_at_original_pos)}"
                #         )
                #         if sig_at_original_pos is sig:
                #             error_message_parts.append(
                #                 "    (Note: This is the same problematic signature object, indicating a sort shift.)")
                #         else:
                #             error_message_parts.append(
                #                 "    (Note: A different signature now occupies the original final_index.)")
                #     else:
                #         error_message_parts.append(
                #             f"  Original final_index {sig.final_index} is currently out of bounds for the list (len: {len(self.all_signatures)})."
                #         )

                #     raise Exception("\n".join(error_message_parts))
                continue

            is_unique_from_prev = (i == 0) or (
                compare_signatures(sig, self.all_signatures[i - 1]) != 0)
            is_unique_from_next = (i == len(self.all_signatures) - 1) or (
                compare_signatures(sig, self.all_signatures[i + 1]) != 0)

            if is_unique_from_prev and is_unique_from_next:
                sig.node.final_index = i
                sig.node.resolution_step = pass_number
                made_progress = True

        return made_progress

    def all_are_finalized(self) -> bool:
        return all(node.is_finalized for node in self.nodes_map.values())

    def expand_ambiguous_nodes(self, pass_number: int) -> bool:
        any_expansion_occurred = False
        for sig_obj in list(self.all_signatures):
            if not sig_obj.is_finalized:
                if self.expand_node(sig_obj, pass_number):
                    any_expansion_occurred = True

        if any_expansion_occurred:
            self.all_signatures.sort()
        return any_expansion_occurred

    def expand_node(self, sig_obj: "NodeSignature", pass_number: int) -> bool:
        if sig_obj.is_loop or sig_obj.is_finalized:
            return False

        any_expansion_occurred = False
        if sig_obj.is_expanded:
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
        max_passes = len(self.graph.nodes()) * 2 + 5
        while pass_number <= max_passes and not self.all_are_finalized():
            made_progress = self.process_pass(pass_number)
            if not made_progress:
                if not self.expand_ambiguous_nodes(pass_number):
                    break
            pass_number += 1
        self.all_signatures.sort()

    def __str__(self) -> str:
        return f"[{','.join(str(sig) for sig in self.all_signatures)}]"

    def sig(self) -> str:
        return f"[{','.join(str(sig.sig()) for sig in self.all_signatures)}]"
