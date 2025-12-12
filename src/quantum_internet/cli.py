"""Command-line helpers for quick network studies."""

from __future__ import annotations

import argparse
from typing import List

from .network import Channel, Node, QuantumNetwork
from .protocols import entangle_path


def build_sample_network() -> QuantumNetwork:
    """Create a small three-node chain useful for sanity checks."""

    network = QuantumNetwork()
    channel = Channel(length_km=10.0, attenuation_db_per_km=0.2, base_fidelity=0.98)
    network.add_path(
        [
            Node(name="alice", memory_size=4, decoherence_rate=0.05),
            Node(name="router", memory_size=2, decoherence_rate=0.1),
            Node(name="bob", memory_size=4, decoherence_rate=0.05),
        ],
        channel_factory=channel,
    )
    return network


def run_cli(args: argparse.Namespace) -> None:
    """Execute the entanglement estimation workflow from CLI arguments."""

    network = build_sample_network()
    path: List[str] = args.path or network.shortest_path("alice", "bob")

    result = entangle_path(
        network,
        path,
        swap_success_prob=args.swap_success_prob,
        swap_fidelity_factor=args.swap_fidelity_factor,
    )
    print("Selected path:", " -> ".join(result.path))
    print(f"Success probability: {result.success_probability:.4e}")
    print(f"Expected attempts: {result.expected_attempts:.2f}")
    print(f"Composite fidelity: {result.composite_fidelity:.4f}")


def parse_args(argv: List[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Quantum internet toy simulator")
    parser.add_argument(
        "--path",
        nargs="+",
        help="Explicit path of node names to entangle (default: shortest path)",
    )
    parser.add_argument(
        "--swap-success-prob",
        type=float,
        default=0.5,
        help=(
            "Per-intermediate-node probability of successful entanglement swap "
            "(default: 0.5)"
        ),
    )
    parser.add_argument(
        "--swap-fidelity-factor",
        type=float,
        default=0.95,
        help=(
            "Multiplicative fidelity factor applied per entanglement swap "
            "(default: 0.95)"
        ),
    )
    return parser.parse_args(argv)


def main(argv: List[str] | None = None) -> None:
    args = parse_args(argv)
    run_cli(args)


if __name__ == "__main__":
    main()
