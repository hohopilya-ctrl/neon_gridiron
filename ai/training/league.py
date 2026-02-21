import sys
import time
import os
import json
import numpy as np
from typing import List, Dict, Optional
from pathlib import Path

from ai.env.neon_env import NeonFootballEnv
from telemetry.logger import UDPSender
from sim.serialization import SimulationEncoder, SimulationRecorder

from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import BaseCallback

class EloRating:
    """Simple Elo rating implementation for agent strength tracking."""
    def __init__(self, initial_elo: float = 1200.0, k_factor: float = 32.0):
        self.rating = initial_elo
        self.k = k_factor

    def expected_score(self, opponent_elo: float) -> float:
        return 1.0 / (1.0 + 10 ** ((opponent_elo - self.rating) / 400.0))

    def update(self, actual_score: float, opponent_elo: float):
        expected = self.expected_score(opponent_elo)
        self.rating += self.k * (actual_score - expected)

class Matchmaker:
    """Manages the pool of agents and match pairings."""
    def __init__(self, model_pool_path: str = "models/pool"):
        self.pool_path = Path(model_pool_path)
        self.pool_path.mkdir(parents=True, exist_ok=True)
        self.agents: Dict[str, EloRating] = {}
        self._load_pool()

    def _load_pool(self):
        # Scan pool for existing models
        for m_path in self.pool_path.glob("*.zip"):
            name = m_path.stem
            self.agents[name] = EloRating()
            # If we had a metadata file with Elos, we'd load it here

    def get_opponent(self, player_elo: float) -> Optional[str]:
        """Returns the name of a suitable opponent from the pool."""
        if not self.agents:
            return None
        # Select opponent with closest Elo (basic matchmaking)
        best_opponent = min(self.agents.keys(), 
                           key=lambda x: abs(self.agents[x].rating - player_elo))
        return best_opponent

    def add_snapshot(self, model, name: str, elo: float):
        path = self.pool_path / f"{name}.zip"
        model.save(str(path))
        self.agents[name] = EloRating(initial_elo=elo)
        print(f"📦 Snapshot saved: {name} (Elo: {elo:.0f})")

class TelemetryCallback(BaseCallback):
    def __init__(self, env, sender, recorder=None, verbose=0):
        super().__init__(verbose)
        self.env = env
        self.sender = sender
        self.recorder = recorder

    def _on_step(self) -> bool:
        # Send telemetry
        self.sender.send_state(self.env)
        # Record frame for replay if enabled
        if self.recorder:
            self.recorder.record_frame(self.env.state)
        return True

def run_league():
    print("🏆 N E O N  U L T R A  L E A G U E  E N G I N E")
    print("---------------------------------------------")
    
    config = {"physics": {"damping": 0.96}}
    env = NeonFootballEnv(config)
    sender = UDPSender()
    
    # Optional: Setup Replay Recording for this training session
    recorder = SimulationRecorder("replays/latest_training.jsonl")
    recorder.start()
    
    matchmaker = Matchmaker()
    
    # Initialize PPO model
    policy_kwargs = dict(net_arch=dict(pi=[256, 256], vf=[256, 256]))
    
    # Try to load latest if exists
    latest_path = "models/ultra_ppo_latest.zip"
    if os.path.exists(latest_path):
        print(f"🔄 Loading existing model: {latest_path}")
        model = PPO.load(latest_path, env=env)
    else:
        model = PPO(
            "MlpPolicy", 
            env, 
            verbose=1, 
            learning_rate=3e-4,
            n_steps=512,
            batch_size=64,
            policy_kwargs=policy_kwargs,
            tensorboard_log="./logs/ppo_neon/"
        )
    
    callback = TelemetryCallback(env, sender, recorder=recorder)
    
    player_elo = EloRating(initial_elo=1500.0) # Baseline for the learner
    
    print(f"🚀 LEAGUE ACTIVE. Current Elo: {player_elo.rating:.0f}")
    
    try:
        gen = 0
        while True:
            gen += 1
            print(f"\n--- Generation {gen} ---")
            
            # 1. Train
            model.learn(total_timesteps=10000, callback=callback, reset_num_timesteps=False)
            
            # 2. Evaluate & Update Elo (Placeholder logic for real evaluation)
            # In a full league, we'd run separate evaluation games here
            player_elo.rating += 15 # Simulated growth
            
            # 3. Snapshot every 5 generations
            if gen % 5 == 0:
                matchmaker.add_snapshot(model, f"agent_gen_{gen}", player_elo.rating)
                model.save("models/ultra_ppo_latest")
                
    except KeyboardInterrupt:
        print("\nShutdown requested. Saving artifacts...")
        model.save("models/ultra_ppo_latest")
        recorder.stop()
        print("✅ Done.")

if __name__ == "__main__":
    # Ensure directories exist
    Path("models/pool").mkdir(parents=True, exist_ok=True)
    Path("replays").mkdir(parents=True, exist_ok=True)
    run_league()
# lines: 50
