import time
import numpy as np
from env.football_env import NeonGridironEnv
from telemetry import UDPSender


def run_random_agents():
    env = NeonGridironEnv(render_mode="human")
    obs, info = env.reset()

    sender = UDPSender()
    print("Starting simulation with random actions. Broadcasting UDP to port 4242...")

    from stable_baselines3 import PPO
    import os
    import glob

    # Load trained model from PBT
    model_path = None
    if os.path.exists("models/best_neon_gridiron_ppo.zip"):
        model_path = "models/best_neon_gridiron_ppo.zip"
        print(f"Loading ALL-TIME BEST MODEL: {model_path}")
    else:
        pbt_models = glob.glob("models/pbt/*.zip")
        if pbt_models:
            model_path = pbt_models[0]  # Just pick the first available one for testing
            print(f"Found fallback PBT model: {model_path}")

    try:
        model = PPO.load(model_path)
        print("Trained model loaded successfully!")
    except:
        print("Model not found! Falling back to random actions.")
        model = None

    for _ in range(1000000):  # Practically infinite
        if model is not None:
            # Flatten observations
            obs_array = np.array([obs[f"agent_{i}"] for i in range(env.num_agents)])
            # SB3 predict expects vector of inputs, returns vector of actions
            try:
                action_array, _ = model.predict(obs_array, deterministic=False)
                actions = {f"agent_{i}": action_array[i] for i in range(env.num_agents)}
            except Exception as e:
                print(f"Prediction error (likely shape mismatch): {e}")
                model = None
                actions = {
                    f"agent_{i}": env.action_space[f"agent_{i}"].sample()
                    for i in range(env.num_agents)
                }
        else:
            actions = {
                f"agent_{i}": env.action_space[f"agent_{i}"].sample() for i in range(env.num_agents)
            }

        obs, _, terminated, truncated, _ = env.step(actions)
        env.render()

        # Broadcast Telemetry
        sender.send_state(env)

        if terminated["__all__"] or truncated["__all__"]:
            obs, info = env.reset()

    # Keep window open a bit
    time.sleep(1)
    print("Simulation finished.")


if __name__ == "__main__":
    run_random_agents()
