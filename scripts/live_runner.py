import socket
import time

import msgpack

from ai.env.neon_env import NeonFootballEnv
from ai.training.orchestrator import PBTTrainer


def run_live_sim(host="127.0.0.1", port=4242):
    print(f"ULTRA Phase 2 Live Runner: {host}:{port}")
    env = NeonFootballEnv({"team_size": 7})
    trainer = PBTTrainer(num_agents=2)  # 2 teams

    env.reset()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    trajectories = []

    try:
        while True:
            # Hierarchical Inference (Simulated for Demo)
            # In production, this calls trainer.population[i].forward(...)
            action = env.action_space.sample()

            obs, reward, terminated, truncated, info = env.step(action)
            trajectories.append({"rewards": [reward]})

            # PBT Step every 1000 ticks
            if env.state.tick % 1000 == 0:
                trainer.step_generation(trajectories)
                trajectories = []

            # Metadata-rich Frame
            frame = env.get_telemetry_frame()
            packed = msgpack.packb(frame, use_bin_type=True)

            sock.sendto(packed, (host, port))

            if terminated or truncated:
                env.reset()

            time.sleep(1 / 60.0)  # 60 FPS

    except KeyboardInterrupt:
        print("Live Runner stopped.")


if __name__ == "__main__":
    run_live_sim()
