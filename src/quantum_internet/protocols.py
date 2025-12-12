"""Protocol-level simulation utilities for entanglement distribution."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List

from .network import QuantumNetwork


@dataclass
class EntanglementResult:
    """Summary statistics for entanglement generation along a path."""

    path: List[str]
    success_probability: float
    expected_attempts: float
    composite_fidelity: float


def entangle_path(
    network: QuantumNetwork,
    path: Iterable[str],
    *,
    swap_success_prob: float = 0.5,
    swap_fidelity_factor: float = 0.95,
) -> EntanglementResult:
    """Estimate entanglement success probability and fidelity along a path.

    The model is intentionally lightweight: each channel contributes an
    independent transmission probability and fidelity. Intermediate entanglement
    swapping steps further attenuate both probability of success and output
    fidelity. By default, each swap is assumed to succeed with probability 0.5
    and to reduce fidelity multiplicatively by 0.95.

    Args:
        network: Quantum network instance containing the path.
        path: Ordered node names describing the route to entangle.
        swap_success_prob: Probability of a successful swap operation at each
            intermediate node (nodes strictly between the endpoints). Must be
            in (0, 1].
        swap_fidelity_factor: Multiplicative fidelity factor applied per swap
            event. Must be in (0, 1].
    """

    node_path = list(path)
    if len(node_path) < 2:
        raise ValueError("Path must contain at least two nodes")
    if not 0.0 < swap_success_prob <= 1.0:
        raise ValueError("swap_success_prob must be in (0, 1]")
    if not 0.0 < swap_fidelity_factor <= 1.0:
        raise ValueError("swap_fidelity_factor must be in (0, 1]")

    num_swaps = max(len(node_path) - 2, 0)

    channel_success_probability = network.path_loss(node_path)
    channel_fidelity = network.path_fidelity(node_path)

    swap_success_total = swap_success_prob ** num_swaps
    swap_fidelity_total = swap_fidelity_factor ** num_swaps

    success_probability = channel_success_probability * swap_success_total
    composite_fidelity = channel_fidelity * swap_fidelity_total

    if success_probability == 0:
        expected_attempts = float("inf")
    else:
        expected_attempts = 1.0 / success_probability

    return EntanglementResult(
        path=node_path,
        success_probability=success_probability,
        expected_attempts=expected_attempts,
        composite_fidelity=composite_fidelity,
    )
