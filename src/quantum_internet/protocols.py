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


def entangle_path(network: QuantumNetwork, path: Iterable[str]) -> EntanglementResult:
    """Estimate entanglement success probability and fidelity along a path.

    The model is intentionally lightweight: each channel contributes an
    independent transmission probability and fidelity. The probability of a
    successful end-to-end entangled pair is the product of hop probabilities,
    and the expected number of attempts is the reciprocal.
    """

    node_path = list(path)
    if len(node_path) < 2:
        raise ValueError("Path must contain at least two nodes")

    success_probability = network.path_loss(node_path)
    composite_fidelity = network.path_fidelity(node_path)

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
