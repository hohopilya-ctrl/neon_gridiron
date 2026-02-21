# Neon Gridiron ULTRA 🏗️⚽

Professional 7v7 Futuristic Football simulation with MARL (Multi-Agent Reinforcement Learning) and Hierarchical Self-Play.

## Project Structure
- `sim/`: Core physics engine (Pymunk) and match logic.
- `ai/`: RL environment (Gymnasium) and neural network policies.
- `server/`: Communication bridge and real-time telemetry.
- `telemetry/`: Structured logging and data broadcasting.
- `godot_client/`: High-performance 3D visualization.
- `ui/`: Web Dashboard and Match Viewer.
- `scripts/`: Development and automation tools.

## Quick Start (Development)
1. **Initialize Environment**:
   ```bash
   # Recommended: Python 3.12+
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Run ULTRA Stack**:
   ```bash
   python run_ultra.py
   ```

3. **Cleanup Artifacts**:
   ```bash
   python scripts/cleanup.py
   ```

## Architecture
The project follows a decoupling principle between **Computation** (Simulation/AI) and **Visualization** (Godot/Web).
Communication is handled via UDP (low-latency telemetry) and WebSockets (state synchronization).

---
*Maintained by Antigravity (Principal AI Engineer)*
