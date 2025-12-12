# quantum-internet-challenge-2025

SquidASM-inspired quantum internet toolkit for the QIA Challenge 2025. The goal
is to provide a lightweight, hackathon-ready scaffold for reasoning about
entanglement distribution on small networks.

## Quick start

1. Install dependencies (uses `networkx` only):

   ```bash
   pip install -r requirements.txt
   ```

2. Run the built-in sample scenario:

   ```bash
   python -m quantum_internet.cli
   ```

   Example output:

   ```
   Selected path: alice -> router -> bob
   Success probability: 6.3096e-02
   Expected attempts: 15.85
   Composite fidelity: 0.0606
   ```

3. Provide a custom path (e.g., when multiple routes exist):

   ```bash
   python -m quantum_internet.cli --path alice router bob
   ```

## Project layout

- `src/quantum_internet/network.py`: Core graph abstractions for nodes and
  channels, including loss/fidelity estimation.
- `src/quantum_internet/protocols.py`: Protocol-level utilities, starting with
  entanglement success estimation.
- `src/quantum_internet/cli.py`: Minimal CLI for running quick network studies.

This scaffold is intentionally dependency-light to stay portable across HPC
clusters and hackathon environments. Extend it with realistic channel models,
link-layer protocols, and scheduling strategies as needed.
