"""Lightweight quantum network modeling utilities.

This module provides simple abstractions for nodes, quantum channels, and
high-level network reasoning. The goal is to offer a portable and dependency-
light baseline that can run in constrained environments (e.g., hackathon
clusters) while still surfacing the key performance characteristics of quantum
links such as loss, latency, and fidelity.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List

import math
import networkx as nx


@dataclass
class Node:
    """Representation of a quantum network node.

    Attributes:
        name: Unique name of the node.
        memory_size: Number of qubits available for entanglement storage.
        decoherence_rate: Characteristic decoherence rate (1/s) for stored
            qubits. A higher rate means faster decay of entanglement fidelity.
    """

    name: str
    memory_size: int = 1
    decoherence_rate: float = 0.0

    def __post_init__(self) -> None:
        if self.memory_size <= 0:
            raise ValueError("memory_size must be positive")
        if self.decoherence_rate < 0:
            raise ValueError("decoherence_rate must be non-negative")


@dataclass
class Channel:
    """Quantum channel connecting two nodes.

    Attributes:
        length_km: Physical length of the channel.
        attenuation_db_per_km: Loss factor per kilometer. Defaults to standard
            telecom fiber (0.2 dB/km).
        base_fidelity: Baseline channel fidelity absent loss.
        depolarizing_prob: Depolarizing noise probability per channel use.
    """

    length_km: float
    attenuation_db_per_km: float = 0.2
    base_fidelity: float = 0.98
    depolarizing_prob: float = 0.0

    def __post_init__(self) -> None:
        if self.length_km <= 0:
            raise ValueError("Channel length must be positive")
        if self.attenuation_db_per_km < 0:
            raise ValueError("Attenuation cannot be negative")
        if not 0.0 < self.base_fidelity <= 1.0:
            raise ValueError("base_fidelity must be in (0, 1]")
        if not 0.0 <= self.depolarizing_prob < 1.0:
            raise ValueError("depolarizing_prob must be in [0, 1)")

    @property
    def transmission_probability(self) -> float:
        """Return the photon transmission probability for the channel.

        Uses an exponential attenuation model: ``P = 10^(-alpha * L / 10)``
        where ``alpha`` is dB/km and ``L`` is the channel length in km.
        """

        loss_db = self.attenuation_db_per_km * self.length_km
        return 10 ** (-loss_db / 10)

    @property
    def fidelity(self) -> float:
        """Approximate end-to-end fidelity after loss and depolarization."""

        loss_factor = self.transmission_probability
        depolarization_factor = 1.0 - self.depolarizing_prob
        return self.base_fidelity * loss_factor * depolarization_factor


@dataclass
class QuantumNetwork:
    """Graph-based quantum network abstraction."""

    nodes: Dict[str, Node] = field(default_factory=dict)
    graph: nx.Graph = field(default_factory=nx.Graph)

    def add_node(self, node: Node) -> None:
        """Add a node to the network, ensuring uniqueness."""

        if node.name in self.nodes:
            raise ValueError(f"Node {node.name!r} already exists")
        self.nodes[node.name] = node
        self.graph.add_node(node.name)

    def add_channel(self, source: str, target: str, channel: Channel) -> None:
        """Connect two existing nodes with a bidirectional quantum channel."""

        if source not in self.nodes or target not in self.nodes:
            raise KeyError("Both source and target must exist before linking")
        if self.graph.has_edge(source, target):
            raise ValueError(f"Channel between {source} and {target} already exists")

        weight = -math.log(channel.transmission_probability)
        self.graph.add_edge(source, target, channel=channel, weight=weight)

    def shortest_path(self, source: str, target: str) -> List[str]:
        """Return the minimum-loss path using Dijkstra on channel weights."""

        self._validate_nodes_exist([source, target])
        return nx.dijkstra_path(self.graph, source, target, weight="weight")

    def path_loss(self, path: Iterable[str]) -> float:
        """Compute total transmission probability along a path."""

        nodes = list(path)
        if len(nodes) < 2:
            raise ValueError("Path must contain at least two nodes")

        probability = 1.0
        for u, v in zip(nodes, nodes[1:]):
            self._ensure_edge(u, v)
            channel: Channel = self.graph[u][v]["channel"]
            probability *= channel.transmission_probability
        return probability

    def path_fidelity(self, path: Iterable[str]) -> float:
        """Estimate composite fidelity along the path."""

        nodes = list(path)
        if len(nodes) < 2:
            raise ValueError("Path must contain at least two nodes")

        fidelity = 1.0
        for u, v in zip(nodes, nodes[1:]):
            self._ensure_edge(u, v)
            channel: Channel = self.graph[u][v]["channel"]
            fidelity *= channel.fidelity
        return fidelity

    def add_path(self, nodes: List[Node], channel_factory: Channel) -> None:
        """Convenience helper to add a linear chain of nodes with identical channels.

        Args:
            nodes: Ordered list of nodes to connect in sequence.
            channel_factory: Channel instance used as a template for each hop.
        """

        if len(nodes) < 2:
            raise ValueError("At least two nodes required to form a path")

        for node in nodes:
            if node.name not in self.nodes:
                self.add_node(node)

        for left, right in zip(nodes, nodes[1:]):
            channel = Channel(
                length_km=channel_factory.length_km,
                attenuation_db_per_km=channel_factory.attenuation_db_per_km,
                base_fidelity=channel_factory.base_fidelity,
                depolarizing_prob=channel_factory.depolarizing_prob,
            )
            self.add_channel(left.name, right.name, channel)

    def _validate_nodes_exist(self, node_names: Iterable[str]) -> None:
        missing = [name for name in node_names if name not in self.nodes]
        if missing:
            raise KeyError(f"Nodes not found: {missing}")

    def _ensure_edge(self, u: str, v: str) -> None:
        if not self.graph.has_edge(u, v):
            raise KeyError(f"Missing channel between {u} and {v}")
