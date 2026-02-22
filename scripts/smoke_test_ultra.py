from ai.env.neon_env import NeonFootballEnv


def smoke_test():
    print("Starting ULTRA Vertical Slice Smoke Test...")
    env = NeonFootballEnv({"seed": 1337})
    obs, info = env.reset()

    print(f"Observation Keys: {obs.keys()}")
    print(f"Ball Obs Shape: {obs['ball'].shape}")
    print(f"Players Obs Shape: {obs['players'].shape}")

    # Run 100 steps
    for i in range(100):
        action = env.action_space.sample()
        obs, reward, terminated, truncated, info = env.step(action)

        if i % 20 == 0:
            frame = env.get_telemetry_frame()
            print(f"Step {i}: Score {frame.s}, Tick {frame.t}")

    print("Smoke Test PASSED ✅")


if __name__ == "__main__":
    smoke_test()
