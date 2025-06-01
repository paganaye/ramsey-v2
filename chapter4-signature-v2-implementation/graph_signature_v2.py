from typing import List, Optional, Tuple, Any
from typing import Dict, List
import networkx as nx
from typing import List
from functools import cmp_to_key

class NodeSignature:
    def __init__(
        self,
        neighborCount: int,
        label: Optional[str] = None,
        finalIndex: Optional[int] = None,
        resolutionStep: Optional[int] = None,
        cycleDistance: Optional[int] = None,
        neighbors: Optional[List["NodeSignature"]] = None,
    ):
        self.label: Optional[str] = label
        self.neighborCount: int = neighborCount
        self.finalIndex: Optional[int] = finalIndex
        self.resolutionStep: Optional[int] = resolutionStep
        self.cycleDistance: Optional[int] = cycleDistance
        self.neighbors: Optional[List["NodeSignature"]] = neighbors


GraphSignature = List[NodeSignature]


def optCompare(a: Optional[int], b: Optional[int]) -> int:
    return (
        0
        if a == b
        else (1 if a is None else (-1 if b is None else (-1 if a < b else 1)))
    )


def compare_signatures(sig_a: NodeSignature, sig_b: NodeSignature) -> int:

    diff_nc = sig_b.neighborCount - sig_a.neighborCount
    if diff_nc != 0:  # 1. By neighborCount (descending)
        return diff_nc

    fi_cmp = optCompare(sig_a.finalIndex, sig_b.finalIndex)
    if fi_cmp != 0:  # 2. Final index
        return fi_cmp

    cd_cmp = optCompare(sig_a.cycleDistance, sig_b.cycleDistance)
    if cd_cmp != 0:  # 3. Cycke distance
        return cd_cmp

    fs_cmp = optCompare(sig_a.resolutionStep, sig_b.resolutionStep)
    if fs_cmp != 0:  # 4. Finish step
        return fs_cmp

    has_n_a = sig_a.neighbors is not None
    has_n_b = sig_b.neighbors is not None

    if has_n_a != has_n_b:
        return -1 if has_n_a else 1  # The one with neighbors (EXPANDED) comes first

    if has_n_a and has_n_b:  # 5. Neighbours
        for i in range(sig_a.neighborCount):
            comparison_result = compare_signatures(
                sig_a.neighbors[i], sig_b.neighbors[i]
            )
            if comparison_result != 0:
                return comparison_result

    # signatures are considered equal for now.
    return 0

def create_initial_signatures(graph: nx.Graph) -> List[NodeSignature]:
    initial_signatures = []
    for node_label in graph.nodes():
        signature = NodeSignature(
            label=str(node_label), # Ensure label is a string
            neighborCount=graph.degree(node_label)
        )
        initial_signatures.append(signature)

    return initial_signatures

def process_signatures_pass(
    signatures: List[NodeSignature], pass_number: int
) -> Tuple[List[NodeSignature], bool]:
    """
    Performs one pass of the signature processing algorithm: sorting and finalizing.
    This corresponds to steps 2 and 3 of Pass 1 in the documentation.

    Args:
        signatures: The current list of NodeSignature objects.
        pass_number: The current pass number (e.g., 1, 2, ...).

    Returns:
        A tuple containing:
        - The list of signatures, sorted and potentially with newly finalized items.
        - A boolean indicating if any new signature was finalized during this pass.
    """
    # 1. Sort the list using the core comparison logic
    signatures.sort(key=cmp_to_key(compare_signatures))

    made_progress = False
    
    # 2. Iterate through the sorted list to find and finalize unique signatures
    for i, sig in enumerate(signatures):
        # Skip if this signature is already finalized
        if sig.finalIndex is not None:
            continue

        # A signature is unique if it's different from its neighbors in the sorted list
        is_unique_from_prev = (i == 0) or (compare_signatures(sig, signatures[i - 1]) != 0)
        is_unique_from_next = (i == len(signatures) - 1) or (compare_signatures(sig, signatures[i + 1]) != 0)

        if is_unique_from_prev and is_unique_from_next:
            sig.finalIndex = i
            sig.resolutionStep = pass_number
            made_progress = True

    return signatures, made_progress