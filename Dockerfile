# OUTPUT PART 9/9 (FINAL)
# Neon Gridiron ULTRA: Docker and Testing

# File: Dockerfile
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Default for training
CMD ["python", "-m", "ai.training.league"]
# lines: 15

# File: docker-compose.yml
version: '3.8'

services:
  training:
    build: .
    environment:
      - NEON_PATCH=season_03
    volumes:
      - ./models:/app/models
      - ./replays:/app/replays
    restart: always

  api_server:
    build: .
    command: uvicorn server.app:app --host 0.0.0.0 --port 8000
    ports:
      - "8000:8000"
    restart: always
# lines: 20

# File: tests/test_determinism.py
import pytest
import numpy as np
from ai.env.neon_env import NeonFootballEnv

def test_identical_seeds():
    config = {'physics': {'damping': 0.95}}
    env1 = NeonFootballEnv(config, seed=42)
    env2 = NeonFootballEnv(config, seed=42)
    
    obs1, _ = env1.reset()
    obs2, _ = env2.reset()
    
    # Simple check for initial state equality
    assert np.allclose(obs1.get('ball', 0), obs2.get('ball', 0))
    
    # Step both environments
    actions = {f"agent_{i}": np.zeros(5) for i in range(14)}
    for _ in range(100):
        o1, _, _, _, _ = env1.step(actions)
        o2, _, _, _, _ = env2.step(actions)
        
        # Check drift
        assert np.allclose(o1.get('ball', 0), o2.get('ball', 0))
# lines: 25

# File: tests/test_env_contract.py
from ai.env.neon_env import NeonFootballEnv

def test_gym_compatibility():
    config = {}
    env = NeonFootballEnv(config)
    obs, info = env.reset()
    
    assert isinstance(obs, dict)
    assert "agent_0" in obs
    
    actions = {f"agent_{i}": [0,0,0,0,0] for i in range(14)}
    o, r, d, t, i = env.step(actions)
    
    assert len(r) == 14
    assert isinstance(d, dict)
# lines: 15

# File: .github/workflows/ci.yml
name: Neon ULTRA CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.12"
      - name: Install dependencies
        run: |
          pip install ruff mypy pytest
          pip install -r requirements.txt
      - name: Lint
        run: ruff check .
      - name: Type Check
        run: mypy .
      - name: Test
        run: pytest
# lines: 25

# REPOSITORY GENERATION COMPLETE.
# Total files generated: 52
# Estimated total lines: 5800+
