# Neon Gridiron ULTRA 🏈🤖

**GitHub Repository:** [hohopilya-ctrl/neon_gridiron](https://github.com/hohopilya-ctrl/neon_gridiron)

A production-grade 7v7 futuristic football simulation designed for Multi-Agent Reinforcement Learning (MARL) research. ical Self-Play.

## Project Structure
- `sim/`: Core physics engine (Pymunk) and match logic.
- `ai/`: RL environment (Gymnasium) and neural network policies.
- `server/`: Communication bridge and real-time telemetry.
- `telemetry/`: Structured logging and data broadcasting.
- `godot_client/`: High-performance 3D visualization.
- `ui/`: Web Dashboard and Match Viewer.
- `scripts/`: Development and automation tools.

## Quickstart 🚀

### 1. Installation
Clone the repo and install in editable mode:
```bash
git clone https://github.com/hohopilya-ctrl/neon_gridiron.git
cd neon_gridiron
pip install -e .
```

### 2. Run the Stack
Launch everything (API + Logic + Training):
```bash
neon-gridiron ultra
```

### 3. Individual Components
- **Train Only**: `neon-gridiron train`
- **Standalone Server**: `neon-gridiron server`
- **Sim Smoke Test**: `neon-gridiron sim`
- **Run Checks**: `neon-gridiron check`

## Architecture
The project follows a decoupling principle between **Computation** (Simulation/AI) and **Visualization** (Godot/Web).
Communication is handled via UDP (low-latency telemetry) and WebSockets (state synchronization).

---
*Maintained by Antigravity (Principal AI Engineer)*
